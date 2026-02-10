from abc import ABC, abstractmethod
import re
import logging
from typing import Any, List, Dict, Optional, Protocol, Tuple

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool

from API.Repository.i_vector_repository import IVectorRepository
from API.Repository.i_sql_repository import ISQLRepository


logger = logging.getLogger(__name__)


class IRAGStrategy(Protocol):
    """Strategy interface for different RAG implementations."""

    def run(
        self,
        vector_repo: IVectorRepository,
        sql_repo: ISQLRepository,
        llm: BaseChatModel,
        course_id: str,
        course: dict,
        student_id: Optional[str],
        question: str,
    ) -> Dict[str, Any]:
        ...


class BaseRAGStrategy(ABC, IRAGStrategy):

    def load_past_messages(self, llm: BaseChatModel, sql_repo: ISQLRepository, course_id: str) -> Tuple[str, List[HumanMessage | AIMessage]]:
        """
        Return a 3–4 sentence summary of past course messages and the raw messages.
        """

        rows = sql_repo.read_all_queries_for_course(course_id, 5)["queries"]
        if not rows:
            return "", []

        past_messages: List[HumanMessage | AIMessage] = []
        transcript_parts: List[str] = []

        # Convert each Q/A into LangChain messages + transcript lines
        for row in reversed(rows):  # oldest → newest
            q = row["query_text"]
            a = row.get("response_text")

            # messages for the LLM
            past_messages.append(HumanMessage(content=q))
            transcript_parts.append(f"Q: {q}")

            if a and a.strip():
                past_messages.append(AIMessage(content=a))
                transcript_parts.append(f"A: {a}")

        return "\n\n".join(transcript_parts), past_messages

    def retrieve_chunks(self, vector_repo: IVectorRepository, course_id: str, question: str) -> Tuple[str, List[str]]:
        """
        Return concatenated chunk text (content) and source summary (artifact).
        """

        retrieved = vector_repo.query(course_id, question, 10)
        if not retrieved:
            return "No content retrieved.", []

        content = "\n\n-----\n\n".join(f"[Chunk {i+1}]\n{doc.page_content}" for i, (doc, _) in enumerate(retrieved))

        unique_sources = {
            f"{doc.metadata.get('source') or doc.metadata.get('file_name') or 'Unknown'}"
            + (f" (page {doc.metadata.get('page')})" if doc.metadata.get("page") else "")
            for doc, _ in retrieved
        }

        return content, sorted(unique_sources)

    def get_course_details(self, course: dict) -> Tuple[str, dict]:
        """
        Return:
        • formatted course metadata as a string (excluding *_id fields)
        • cleaned metadata dict without *_id fields
        """
        return "\n".join(f"{k}: {v}" for k, v in course.items() if not k.endswith("_id")), course
    
    def clean_llm_output(self, text: str) -> str:
        """
        """
        cleaned = text

        # Remove <think>...</think> reasoning blocks
        cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        return cleaned.strip()

    @abstractmethod
    def run(
        self,
        vector_repo,
        sql_repo,
        llm,
        course_id: str,
        course: dict,
        student_id: Optional[str],
        question: str,
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
        student_id: Optional[str],
        question: str,
    ) -> Dict[str, Any]:
        
        logger.info(f"[SimpleRAG] ---- START question={question!r} ----")

        retrieved_content, retrieved_sources = self.retrieve_chunks(vector_repo, course_id, question)
        logger.info(f"[SimpleRAG] Sources found")

        summarized_past_messages, past_messages = self.load_past_messages(llm, sql_repo, course_id)
        logger.info(f"[SimpleRAG] Loaded past messages")

        course_metadata, course_object = self.get_course_details(course)
        logger.info(f"[SimpleRAG] Gotten Course metadata")

        # 3. Build message sequence
        messages = [
            SystemMessage(content=(
                "You are CourseGPT, an AI assistant for a specific college course.\n"
                "Answer using only the following:\n"
                "• retrieved course materials\n"
                "• provided course metadata\n"
                "• past conversation\n\n"

                "If the retrieved course material does not contain relevant information,\n"
                "you MUST reply exactly with:\n"
                "\"I don’t have enough course information to answer that.\"\n\n"

                "Do NOT use outside knowledge.\n"
                "Do NOT infer.\n"
                "Be accurate, concise, and avoid hallucination.\n\n"

                "STRICT OUTPUT RULES:\n"
                "- NEVER mention chunk numbers or headers (e.g., \"[Chunk 1]\").\n"
                "- NEVER mention file names, sources, or page numbers.\n"
                "- NEVER say where you got the information from.\n"
                "- NEVER mention \"retrieved materials\" or \"course metadata\".\n"
                "- ONLY return a clean, natural-language answer.\n"
            )),
            SystemMessage(content=f"### CourseGPT Course Profile\n{course_metadata}"),
            SystemMessage(content=f"### Retrieved Course Material\n{retrieved_content}"),
            *past_messages,
            HumanMessage(content=question)
        ]

        result = llm.invoke(messages)
        answer = self.clean_llm_output(result if isinstance(result, str) else result.content)
        logger.info("[SimpleRAG] LLM call complete")

        sql_repo.create_query(student_id, course_id, query_text=question, response_text=answer)
        logger.info(f"[SimpleRAG] Stored query in DB for student_id={student_id}")

        logger.info(f"[SimpleRAG] ---- END question ----")
        return {
            "answer": answer,
            "sources": retrieved_sources if answer != "I don’t have enough course information to answer that." and retrieved_sources else []
        }


class AgenticRAGStrategy(BaseRAGStrategy):
    def run(
        self,
        vector_repo: IVectorRepository,
        sql_repo: ISQLRepository,
        llm: BaseChatModel,
        course_id: str,
        course: dict,
        student_id: Optional[str],
        question: str,
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
            "    \"I don’t have enough course information to answer that.\"\n"
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

        retrieved_sources = sorted({src for msg in messages if isinstance(msg, ToolMessage) and msg.name == "tool_retrieve_chunks" for src in (msg.artifact or [])})

        sql_repo.create_query(student_id, course_id, query_text=question, response_text=clean_answer)
        logger.info(f"[AgenticRAG] Stored query in DB for student_id={student_id}")

        logger.info(f"[AgenticRAG] ---- END question ----")
        return {
            "answer": clean_answer,
            "sources": retrieved_sources if clean_answer != "I don’t have enough course information to answer that." and retrieved_sources else [],
            "reasoning": clean_reasoning
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
