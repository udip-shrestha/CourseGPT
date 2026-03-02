from abc import ABC, abstractmethod
import re
import logging
from typing import Any, List, Dict, Optional, Protocol, Tuple, runtime_checkable
from datetime import datetime
import json

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

        chunks = []
        sources = []

        for doc, score in results:
            chunks.append(doc.page_content)

            title = (
                doc.metadata.get("title")
                or doc.metadata.get("file_name")
                or "Unknown"
            )

            if title not in sources:
                sources.append(title)

        content = "\n\n".join(chunks)

        return content, sources
        

    # -----------------------------
    # Multi-Query Expansion
    # -----------------------------
    def expand_query(self, llm: BaseChatModel, question: str) -> List[str]:
        prompt = [
            SystemMessage(content=(
                "You are a query expansion assistant for a college course search engine.\n"
                "Generate 3 alternative search queries for the student question.\n"
                "Focus on academic keywords like policy, rubric, deadline, requirement, concept.\n"
                "Return ONLY the 3 queries, one per line."
            )),
            HumanMessage(content=question)
        ]

        result = llm.invoke(prompt)
        text = result if isinstance(result, str) else result.content

        return [q.strip() for q in text.split("\n") if q.strip()]
    
    # -----------------------------
    # Reranking
    # -----------------------------
    def rerank_chunks(
        self,
        llm: BaseChatModel,
        question: str,
        chunks: List[dict],
        top_k: int = 4
    ) -> List[dict]:

        if not chunks:
            return []

        scored = []

        for chunk in chunks:
            prompt = [
                SystemMessage(content="Score relevance from 1-10. Return ONLY a number."),
                HumanMessage(content=f"Question: {question}\n\nChunk:\n{chunk['content']}")
            ]

            result = llm.invoke(prompt)
            score_text = result if isinstance(result, str) else result.content

            try:
                score = float(score_text.strip())
            except:
                score = 5.0

            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in scored[:top_k]]

    # -----------------------------
    # Formatting
    # -----------------------------
    def format_chunks(self, chunks: List[dict]) -> str:
        formatted = ""
        for chunk in chunks:
            formatted += (
                f"Source: {chunk.get('source_type', 'Unknown')} | "
                f"Title: {chunk.get('title', 'Untitled')} | "
                f"Date: {chunk.get('date', 'Unknown')}\n"
                f"{chunk['content']}\n\n"
            )
        return formatted
    
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

        # retrieved_content, retrieved_sources = self.retrieve_chunks(vector_repo, course_id, question)
        # logger.info(f"[SimpleRAG] Sources found")

        # course_metadata, course_object = self.get_course_details(course)
        # logger.info(f"[SimpleRAG] Gotten Course metadata")

        # ------------------------------
        # Query Classification
        # ------------------------------
        classification_prompt = [
            SystemMessage(content=(
                "Classify the student query into one of these categories.\n"
                "Respond ONLY with valid JSON:\n"
                "{\n"
                '  "query_type": '
                '"concept_explanation" | '
                '"homework_help" | '
                '"study_plan" | '
                '"exam_preparation" | '
                '"logistics" | '
                '"policy_query" | '
                '"technical_support" | '
                '"contact_info" | '
                '"general_chat" | '
                '"other"\n'
                "}\n\n"

                "Category Definitions:\n"
                "- logistics: deadlines, due dates, submission methods, assignment timing.\n"
                "- policy_query: grading policy, attendance rules, late penalties.\n"
                "- technical_support: lab errors, setup issues, coding problems.\n"
                "- contact_info: instructor email, office hours, TA availability.\n"
                "- general_chat: greetings or casual conversation.\n"
            )),
            HumanMessage(content=question)
        ]


        result = llm.invoke(classification_prompt)
        text = result if isinstance(result, str) else result.content

        try:
            classification_data = json.loads(text)
            query_type = classification_data.get("query_type", "concept_explanation")
        except Exception:
            query_type = "concept_explanation"

        # Guard against unexpected category names
        valid_types = {
            "concept_explanation",
            "homework_help",
            "study_plan",
            "exam_preparation",
            "logistics",
            "policy_query",
            "technical_support",
            "contact_info",
            "general_chat",
            "other"
        }

        if query_type not in valid_types:
            logger.warning(f"[SimpleRAG] Invalid query_type returned: {query_type}")
            query_type = "concept_explanation"

        logger.info(f"[SimpleRAG] Classified as: {query_type}")

        # ------------------------------
        # 2. EARLY EXIT FOR GENERAL CHAT
        # ------------------------------
        if query_type == "general_chat":
            return {
                "answer": "Hello! I'm CourseGPT. Ask me anything about this course.",
                "sources": []
        }


        # ---------------------------------------------------
        # Retrieval
        # ---------------------------------------------------

        retrieved_content, retrieved_sources = self.retrieve_chunks(
            vector_repo, course_id, question
        )

        if not retrieved_content:
            answer = "I don’t have enough course information to answer that."
            sql_repo.create_query(
                student_id,
                course_id,
                query_text=question,
                response_text=answer
            )
            return {
                "answer": answer,
                "sources": []
            }

        # ---------------------------------------------------
        # Metadata + Date Injection
        # ---------------------------------------------------
        course_metadata, _ = self.get_course_details(course)
        current_date = datetime.now().strftime("%A, %B %d, %Y")



        # 3. Build message sequence
        messages = [
            SystemMessage(content=(
                "You are CourseGPT, a knowledgeable, professional and encouraging AI Teaching Assistant. "
                "Your goal is to provide high-quality support using ONLY the provided course materials.\n\n"

                "### CONSTRAINTS (Strictly Enforced)\n"
                "1. GROUNDING: Use only retrieved course materials, metadata, and conversation history. Do not use external knowledge or your own training data.\n"
                "2. UNCERTAINTY: If information is missing, reply EXACTLY with: 'I don’t have enough course information to answer that.'\n"
                "3. PARTIAL INFO: If you have some info but lack specifics (e.g., a room number), provide what you know and state: 'The specific [detail] is not mentioned in the materials.'\n"
                "4. NO INFERENCE: Answer only the exact question asked. Do not guess, speculate, or infer beyond the text.\n\n"

                "### COMMUNICATION STYLE\n"
                "- TONE: Natural, human-like, and direct. Avoid being overly robotic.\n"
                "- CLEAN OUTPUT: NEVER mention file names, page numbers, 'chunks', 'metadata', or 'retrieved materials'.\n"
                "- ANONYMITY: Do not say 'According to the document...' or 'Based on my search...'. Simply state the facts.\n"
                "- RELEVANCE: For general greetings or questions about the instructor, answer naturally without citing the lack of 'retrieved materials'.\n\n"

                "### INTERNAL VERIFICATION\n"
                "Before outputting, verify: Is every claim supported by the context? Are there any source references or chunk IDs? If yes, remove them and rewrite to be clean and natural."
            )),

            SystemMessage(content=(
                "### SPECIALIZED OUTPUT STRUCTURES\n" + (
                    "For HOMEWORK HELP:\n"
                    "1. CONCEPT: Identify the underlying principle.\n"
                    "2. PRINCIPLE: Explain that principle clearly.\n"
                    "3. GUIDANCE: Provide a guiding hint to help them progress.\n"
                    "4. LIMIT: Do NOT provide the final solution or numerical answer.\n"
                    if query_type == "homework_help"
                    else
                    "For STUDY PLANS:\n"
                    "1. STUDY GOAL\n"
                    "2. DAILY BREAKDOWN\n"
                    "3. PRACTICE STRATEGY\n"
                    "4. MILESTONE CHECK\n"
                    if query_type == "study_plan"
                    else
                    "For CONCEPT/EXAM PREP:\n"
                    "1. DEFINITION (What is it?)\n"
                    "2. INTUITION (Why does it work?)\n"
                    "3. EXAMPLE (Applied context)\n"
                    "4. PRACTICE (A quick self-check question)\n"
                    if query_type in ["concept_explanation", "exam_preparation"]
                    else
                    "For LOGISTICS/DEADLINES:\n"
                    "1. KEY DATES: List the relevant deadlines.\n"
                    "2. SUBMISSION METHOD: Explain how to turn it in.\n"
                    "3. LATE POLICY: State the penalty for missing the date.\n"
                    if query_type == "logistics"
                    else

                    "For SYLLABUS/POLICIES:\n"
                    "1. POLICY SUMMARY: State the rule clearly.\n"
                    "2. GRADING IMPACT: Explain how this affects the student's grade.\n"
                    "3. EXCEPTIONS: Mention any documented 'if/then' scenarios.\n"
                    if query_type == "policy_query"
                    else

                    "For TECHNICAL/LAB SUPPORT:\n"
                    "1. TROUBLESHOOTING: Provide a step-by-step checklist.\n"
                    "2. COMMON ERRORS: Mention known issues from the course notes.\n"
                    "3. SUPPORT: Tell them where to post if the issue persists.\n"
                    if query_type == "technical_support"
                    else

                    "For OFFICE HOURS/CONTACT:\n"
                    "1. PERSONNEL: List who is available (Professor/TA).\n"
                    "2. SCHEDULE: Days and times.\n"
                    "3. LOCATION: Physical room or meeting link.\n"
                    if query_type == "contact_info"
                    else ""
                )
            )),
            SystemMessage(content=f"Current Date: {current_date}"),
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
            required_sections = ["CONCEPT", "GUIDANCE"]
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
