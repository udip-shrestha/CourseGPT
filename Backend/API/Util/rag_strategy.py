from abc import ABC, abstractmethod
import re
import logging
from typing import Any, List, Dict, Optional, Protocol, Tuple, runtime_checkable

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool

from API.Repository.i_vector_repository import IVectorRepository
from API.Repository.i_sql_repository import ISQLRepository


logger = logging.getLogger(__name__)


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
        student_id: Optional[str],
        question: str,
    ) -> Dict[str, Any]:
        ...


class BaseRAGStrategy(ABC, IRAGStrategy):

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

        course_metadata, course_object = self.get_course_details(course)
        logger.info(f"[SimpleRAG] Gotten Course metadata")

        # ------------------------------
        # Query Classification
        # ------------------------------
        classification_prompt = [
            SystemMessage(content=(
                "Classify the student query into one of these categories.\n"
                "Respond ONLY with valid JSON:\n"
                "{\n"
                '  "query_type": "concept_explanation" | '
                '"homework_help" | '
                '"study_plan" | '
                '"exam_preparation" | '
                '"general_course_info" | '
                '"other"\n'
                "}\n"
            )),
            HumanMessage(content=question)
        ]


        classification_result = llm.invoke(classification_prompt)
        classification_text = classification_result if isinstance(classification_result, str) else classification_result.content

        try:
            import json
            classification_data = json.loads(classification_text)
            query_type = classification_data.get("query_type", "concept_explanation")
        except Exception:
            query_type = "concept_explanation"

        logger.info(f"[SimpleRAG] Classified as: {query_type}")



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

            SystemMessage(content=(
                "ADDITIONAL OUTPUT STRUCTURE RULES:\n"
                + (
                    "For homework help:\n"
                    "1. APPROACH\n"
                    "2. HINTS\n"
                    "3. KEY CONCEPTS\n"
                    "4. PRACTICE PROBLEM\n"
                    "Do NOT provide final answers.\n\n"
                    if query_type == "homework_help"
                    else
                    "For study plans:\n"
                    "1. STUDY GOAL\n"
                    "2. DAILY BREAKDOWN\n"
                    "3. PRACTICE STRATEGY\n"
                    "4. MILESTONE CHECK\n\n"
                    if query_type == "study_plan"
                    else
                    "For concept explanations or exam preparation:\n"
                    "1. DEFINITION\n"
                    "2. INTUITION\n"
                    "3. EXAMPLE\n"
                    "4. PRACTICE\n\n"
                    if query_type in ["concept_explanation", "exam_preparation"]
                    else
                    ""
                )
            )),
   
            SystemMessage(content=f"### CourseGPT Course Profile\n{course_metadata}"),
            SystemMessage(content=f"### Retrieved Course Material\n{retrieved_content}"),
            HumanMessage(content=question)
        ]

        result = llm.invoke(messages)
        answer = self.clean_llm_output(result if isinstance(result, str) else result.content)

        # ------------------------------
        # Structured Output Validation
        # ------------------------------

        if query_type in ["concept_explanation", "exam_preparation"]:
            required_sections = ["DEFINITION", "EXAMPLE"]
        elif query_type == "homework_help":
            required_sections = ["APPROACH", "HINTS"]
        elif query_type == "study_plan":
            required_sections = ["STUDY GOAL", "DAILY"]
        else:
            required_sections = []

        if required_sections and not all(section in answer for section in required_sections):
            logger.warning(
                f"[SimpleRAG] Structured format missing sections for type={query_type}"
            )



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
