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
            formatted_chunks.append(f"[{chunk_id}]: {chunk.page_content}")

            title = chunk.metadata.get("title") or chunk.metadata.get("file_name") or "Unknown"
            if title not in sources:
                sources.append(title)

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

        if not retrieved_content:
            answer = NO_ANSWER_RESPONSE
            if not validate: sql_repo.create_query(student_id, course_id, query_text=question, response_text=answer)
            return {"strategy": self.__class__.__name__, "answer": answer, "sources": [], "chunks": None if not validate else []}

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
                "You are CourseGPT, a knowledgeable, professional and encouraging AI Teaching Assistant. "
                "Your goal is to provide answer to STUDENT QUESTION using ONLY the provided course materials.\n\n"

                "### CONSTRAINTS (Strictly Enforced)\n"
                "1. GROUNDING: Use only the retrieved course materials and metadata to answer STUDENT QUESTION. Do not use external knowledge.\n"
                f"2. NO ANSWER RULE (HIGHEST PRIORITY): If the answer to STUDENT QUESTION cannot be reasonably found or inferred from the retrieved materials, reply EXACTLY with: '{NO_ANSWER_RESPONSE}'. "
                "You may synthesize an answer from information clearly present in the text, including drawing direct conclusions from stated facts."
                "3. STRICT REFUSAL FORMAT: If rule 2 applies, output ONLY the exact sentence above with no additional words, explanations, or changes.\n"
                "4. NO INFERENCE: Do not guess, assume, or infer missing details about STUDENT QUESTION. Only use explicitly stated information.\n"
                "5. RELEVANCE CHECK: If the retrieved content is not clearly relevant to the STUDENT QUESTION, treat it as missing information and apply rule 2.\n"
                "6. SCOPE LIMIT: Answer only the specific STUDENT QUESTION asked. Do not add unrelated context, examples, background, commentary, or follow-up explanation unless the question explicitly asks for it.\n"
                "7. STOP RULE: Once the question has been directly and sufficiently answered, stop immediately and do not add any additional sentences.\n"
                "8. CONCISENESS: Prefer the shortest complete answer that fully answers the question.\n"

                "### COMMUNICATION STYLE\n"
                "- When applying rule 2 (NO ANSWER RULE), IGNORE all style guidance and follow the exact output requirement strictly.\n"
                "- When answering normally, be natural, human-like, and direct, and concise.\n"
                "- Do not include extra explanation beyond what is needed to answer the question.\n"
                "- CLEAN OUTPUT: NEVER mention file names, page numbers, 'chunks', 'metadata', or 'retrieved materials'.\n"
                "- ANONYMITY: Do not say 'According to the document...' or 'Based on my search...'. Simply state the facts.\n"

                "### INTERNAL VERIFICATION\n"
                "Before outputting, verify: Is every claim supported by the context? Are there any source references or chunk IDs? If yes, remove them and rewrite to be clean and natural."
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
            "sources": retrieved_sources if answer != NO_ANSWER_RESPONSE and retrieved_sources else [],
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
