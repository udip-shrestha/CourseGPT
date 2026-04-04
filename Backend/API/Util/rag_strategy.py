from abc import ABC, abstractmethod
import re
import logging
from typing import Any, List, Dict, Optional, Protocol, Tuple, runtime_checkable
from datetime import datetime

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool

from API.Repository.i_vector_repository import IVectorRepository
from API.Repository.i_sql_repository import ISQLRepository


logger = logging.getLogger(__name__)
NO_ANSWER_RESPONSE = "I do not have enough course information to answer that."


@runtime_checkable
class IRAGStrategy(Protocol):
    """Strategy interface for different RAG implementations."""

    def run(
        self,
        vector_repo: IVectorRepository,
        sql_repo: ISQLRepository,
        llm: BaseChatModel,
        course_id: str,
        course: dict,
        question: str,
        validate: bool = False,
        student_id: Optional[str] = None
    ) -> Dict[str, Any]:
        ...


class BaseRAGStrategy(ABC, IRAGStrategy):

    # -----------------------------
    # Retrieval
    # -----------------------------
    def retrieve_chunks(
        self,
        vector_repo,
        course_id: str,
        question: str,
        k: int = 8,
    ):
        results = vector_repo.query(course_id, question, k)

        if not results:
            return "", []

        sources = []
        formatted_chunks = []

        for chunk_id, chunk in results:
            title = chunk.metadata.get("source") or chunk.metadata.get("title") or chunk.metadata.get("file_name") or "Unknown"
            if title != "Unknown" and title not in sources:
                sources.append(title)

            formatted_chunks.append(f"[Source: {title} | Chunk: {chunk_id}]\n{chunk.page_content}")

        content = "\n\n".join(formatted_chunks)

        return content, sources

    # -----------------------------
    # Metadata
    # -----------------------------
    def get_course_details(self, course: dict) -> Tuple[str, dict]:
        """
        Return:
        • formatted course metadata as a string (excluding *_id fields)
        • cleaned metadata dict without *_id fields
        """
        return "\n".join(f"{k}: {v}" for k, v in course.items() if not k.endswith("_id")), course
    
    # -----------------------------
    # Cleaning
    # -----------------------------
    def clean_llm_output(self, text: str) -> str:
        cleaned = re.sub(
            r"<think>.*?</think>",
            "",
            text,
            flags=re.DOTALL | re.IGNORECASE
        )
        return cleaned.strip()
    
    @abstractmethod
    def run(
        self,
        vector_repo,
        sql_repo,
        llm,
        course_id: str,
        course: dict,
        question: str,
        validate: bool = False,
        student_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Subclasses must implement."""
        raise NotImplementedError


class SimpleRAGStrategy(BaseRAGStrategy):

    def run(
        self,
        vector_repo,
        sql_repo,
        llm,
        course_id: str,
        course: dict,
        question: str,
        validate: bool = False,
        student_id: Optional[str] = None
    ) -> Dict[str, Any]:
        
        logger.info(f"[SimpleRAG] ---- START question={question!r} ----")

        # ---------------------------------------------------
        # Retrieval
        # ---------------------------------------------------

        retrieved_content, retrieved_sources = self.retrieve_chunks(
            vector_repo, course_id, question
        )

        # ---------------------------------------------------
        # Metadata + Date Injection
        # ---------------------------------------------------
        course_metadata, _ = self.get_course_details(course)
        current_date = datetime.now().strftime("%A, %B %d, %Y")

        # ---------------------------------------------------
        # Build Message Sequence
        # ---------------------------------------------------
        
        messages = [
            SystemMessage(content=(
                "You are CourseGPT, an AI Teaching Assistant. Answer the STUDENT QUESTION accurately and concisely.\n\n"

                "Follow this decision order exactly and stop at the first matching case:\n\n"

                "A) If COURSE METADATA directly answers the question, answer from metadata only.\n"
                "   Do not add any disclaimer.\n\n"

                "B) Otherwise, if RETRIEVED COURSE MATERIAL contains any information that is topically relevant to the question,\n"
                "   answer using only that material.\n"
                "   - Topically relevant means it discusses the same topic, even if only partially.\n"
                "   - You may restate, summarize, combine, or make a small direct inference from the material.\n"
                "   - Do not add any disclaimer.\n"
                "   - Do not use outside knowledge.\n\n"

                "C) Otherwise, if the question asks for a course-specific fact that is missing from both metadata and retrieved material\n"
                "   (for example: due date, exam room, grading rule, office hours, textbook, policy, logistics), respond with exactly:\n"
                "   This information is not available in the specific course material.\n\n"

                "D) Otherwise, if the question is general or conceptual and neither metadata nor retrieved material contains relevant information,\n"
                "   begin with exactly:\n"
                "   This is based on general knowledge, not specific course material.\n"
                "   Then answer using general knowledge.\n\n"

                "Important rules:\n"
                "- If retrieved material is topically relevant at all, use B, not D.\n"
                "- Do not say information is unavailable if metadata or retrieved material supports an answer.\n"
                "- Do not add unsupported facts.\n"
                "- Do not mention metadata, retrieved material, chunk IDs, file names, or the retrieval process.\n"
                "- Answer only what was asked.\n"
                "- Be concise.\n"
            )),
            SystemMessage(content=f"### STUDENT QUESTION\n{question}"),
            SystemMessage(content=f"Current Date: {current_date}"),
            SystemMessage(content=f"### CourseGPT Course Profile\n{course_metadata}"),
            SystemMessage(content=(
                "### Retrieved Course Material\n"
                "Some retrieved content may be irrelevant. Use ONLY the portions that directly answer the STUDENT QUESTION. Ignore the rest completely.\n\n"
                f"{retrieved_content}"
            )),
            HumanMessage(content=question)
        ]

        # ---------------------------------------------------
        # Invoke LLM
        # ---------------------------------------------------
        
        result = llm.invoke(messages)
        answer = self.clean_llm_output(result if isinstance(result, str) else result.content)
        logger.info("[SimpleRAG] LLM call complete")

        # ---------------------------------------------------
        # Store query in DB
        # ---------------------------------------------------

        if not validate:
            sql_repo.create_query(student_id, course_id, query_text=question, response_text=answer)
            logger.info(f"[SimpleRAG] Stored query in DB for student_id={student_id}")


        logger.info(f"[SimpleRAG] ---- END question ----")
        return {
            "strategy": self.__class__.__name__,
            "answer": answer,
            "sources": retrieved_sources,
            "chunks": [retrieved_content] if validate else None
        }


class AgenticRAGStrategy(BaseRAGStrategy):
    def run(
        self,
        vector_repo: IVectorRepository,
        sql_repo: ISQLRepository,
        llm: BaseChatModel,
        course_id: str,
        course: dict,
        question: str,
        validate: bool = False,
        student_id: Optional[str] = None
    ) -> Dict[str, Any]:
        
        logger.info(f"[AgenticRAG] ---- START question={question!r} ----")
        
        @tool(response_format="content_and_artifact")
        def tool_course_details() -> Tuple[str, dict]:
            """Return formatted course metadata."""
            logger.info(f"[AgenticRAG] Getting Course metadata")
            return self.get_course_details(course)

        @tool(response_format="content_and_artifact")
        def tool_retrieve_chunks(question: str) -> Tuple[str, List[str]]:
            """Retrieve vector chunks relevant to the user's question."""
            logger.info(f"[AgenticRAG] Retrieving relevant chunks")
            return self.retrieve_chunks(vector_repo, course_id, question)

        tools = [
            tool_course_details,
            tool_retrieve_chunks,
        ]

        system_prompt = (
            "You are CourseGPT, an AI assistant for a specific college course.\n"
            "You must answer using ONLY information retrieved through the provided tools.\n"
            "\n"
            "Your goal is to help students and instructors by grounding every answer entirely in\n"
            "stored course materials or stored course metadata. If the required information is\n"
            "not available from the tools, say so clearly.\n"
            "\n"
            "======================\n"
            "TOOLS\n"
            "======================\n"
            "\n"
            "1. retrieve_chunks(question: str)\n"
            "   - Use this for ANY question about course content:\n"
            "       • definitions, theorems, concepts\n"
            "       • examples, steps, procedures\n"
            "       • formulas, derivations\n"
            "       • lecture or reading details\n"
            "   - You may call this multiple times.\n"
            "\n"
            "2. course_details()\n"
            "   - Use this for ANY question about course metadata:\n"
            "       • instructor, term, title, schedule, summary\n"
            "\n"
            "======================\n"
            "BEHAVIORAL GUIDELINES\n"
            "======================\n"
            "\n"
            "- For almost all course-content questions, you SHOULD:\n"
            "    1) Call `retrieve_chunks` with a focused query.\n"
            "    2) Read the returned snippets carefully.\n"
            "    3) Answer using only that retrieved information.\n"
            "    4) You may call `retrieve_chunks` again with different queries if needed.\n"
            "\n"
            "- When the question is about general course information, you SHOULD:\n"
            "    • Call `course_details` to retrieve metadata such as:\n"
            "        - course title, term, instructor\n"
            "        - section, schedule, high-level descriptions\n"
            "        - any general course attributes stored in metadata\n"
            "    • Do NOT answer course-info questions unless supported by `course_details`.\n"
            "\n"
            "- NEVER fabricate details.\n"
            "- NEVER rely on general world knowledge.\n"
            "- STRICT RULE:\n"
            "    If the retrieved course material and course metadata do not contain relevant information, you MUST reply exactly with:\n"
            f"    \"{NO_ANSWER_RESPONSE}\"\n"
            "    Do NOT use outside knowledge.\n"
            "    Do NOT infer.\n"
            "    Do NOT guess.\n"
            "\n"
            "======================\n"
            "ANSWERING STYLE\n"
            "======================\n"
            "\n"
            "- Keep the answer focused strictly on the user's question.\n"
        )

        agent = create_agent(llm, tools, system_prompt=system_prompt)
        events = list(agent.stream({"messages": [HumanMessage(content=question)]}, stream_mode="updates"))
        logger.info("[AgenticRAG] Agent call complete")

        messages = [msg for ev in events for key in ("model", "tools") if key in ev for msg in ev[key]["messages"]]

        clean_reasoning = [
            {
                **({"type": msg.type} if hasattr(msg, "type") and msg.type else {}),
                **({"content": msg.content} if hasattr(msg, "content") and msg.content else {}),
                **({"tool_name": msg.name} if hasattr(msg, "name") and msg.name else {}),
                **({"tool_call": msg.tool_calls} if hasattr(msg, "tool_calls") and msg.tool_calls else {})
            }
            for msg in messages
        ]

        ai_messages = [m for m in messages if isinstance(m, AIMessage)]
        answer = ai_messages[-1].content if ai_messages else ""
        clean_answer = self.clean_llm_output(answer)

        retrieved_contents = [msg.content for msg in messages if isinstance(msg, ToolMessage) and msg.name == "tool_retrieve_chunks"]
        retrieved_sources = sorted({src for msg in messages if isinstance(msg, ToolMessage) and msg.name == "tool_retrieve_chunks" for src in (msg.artifact or [])})

        if not validate:
            sql_repo.create_query(student_id, course_id, query_text=question, response_text=clean_answer)
            logger.info(f"[AgenticRAG] Stored query in DB for student_id={student_id}")

        logger.info(f"[AgenticRAG] ---- END question ----")
        return {
            "strategy": self.__class__.__name__,
            "answer": clean_answer,
            "sources": retrieved_sources if clean_answer != NO_ANSWER_RESPONSE and retrieved_sources else [],
            "reasoning": clean_reasoning,
            "chunks": retrieved_contents if validate else None
        }


STRATEGY_CLASS_REGISTRY: Dict[str, type[IRAGStrategy]] = {
    "SimpleRAGStrategy": SimpleRAGStrategy,
    "AgenticRAGStrategy": AgenticRAGStrategy,
}


class RAGStrategyFactory:
    """Factory that delegates prompt creation by type."""

    def __init__(self, registry: Optional[Dict[str, IRAGStrategy]]=None):
        self._registry = registry or { k: v() for k, v in STRATEGY_CLASS_REGISTRY.items() }

    def get(self, rag_strategy_id: str) -> IRAGStrategy:
        rag_strategy_id = str(rag_strategy_id)
        if rag_strategy_id not in self._registry:
            raise ValueError(f"Unknown RAG strategy id: {rag_strategy_id}")
        return self._registry[rag_strategy_id]
