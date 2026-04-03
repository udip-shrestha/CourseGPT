import json
import os
import re
import time
from typing import Any

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import requests
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel


load_dotenv()


def normalize(text: str) -> str:
    return " ".join(text.lower().split())

def save_json(file_path: str, content: dict) -> None:
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(content, file, indent=2)





def call_query_endpoint(course_id: str, question: str) -> tuple[int, dict[str, Any]]:
    BASE_URL = f"http://{os.environ['API_HOST']}:{os.environ['API_PORT']}"

    TIMEOUT_SECONDS = 60
    url = f"{BASE_URL}/courses/{course_id}/queries"
    params = {
        "question": question,
        "validate": "true",
    }

    start = time.perf_counter()
    response = requests.post(url, params=params, headers={"accept": "application/json"}, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    try:
        payload = response.json()
    except Exception:
        payload = {"raw_text": response.text}

    return elapsed_ms, payload





def get_llm() -> BaseChatModel | None:
    try:
        llm_provider = os.environ["LLM_PROVIDER"].lower()
        print(f"[LLM] LLM_PROVIDER detected as {llm_provider}.")

        if llm_provider == "huggingface":
            model_id, token = os.environ["LLM_MODEL"], os.environ["HUGGINGFACEHUB_API_TOKEN"]
            print(f"[LLM INIT] Initializing HuggingFace Chat Model ID: {model_id}")
            
            endpoint = HuggingFaceEndpoint(
                repo_id=model_id,
                task="text-generation",
                max_new_tokens=512,
                do_sample=False,
                repetition_penalty=1.03,
                temperature=0.0,
                provider="auto"
            )

            return ChatHuggingFace(llm=endpoint)

        if llm_provider == "ollama":
            model_name, base_url = os.environ["LLM_MODEL"], os.environ["LLM_BASE_URL"]
            print(f"[LLM INIT] Initializing Ollama model '{model_name}' at {base_url}")
            return ChatOllama(model=model_name, base_url=base_url, temperature=0)

        if llm_provider == "vllm":
            model_name = os.environ["LLM_MODEL"]
            base_url = os.environ["LLM_BASE_URL"]
            print(f"[LLM INIT] Initializing vLLM model '{model_name}' at {base_url}")

            return ChatOpenAI(model=model_name, base_url=base_url, api_key="EMPTY", temperature=0, max_tokens=1024)

        raise ValueError(f"Unknown LLM_PROVIDER: {llm_provider}")
    
    except Exception as e:
        print(f"[LLM INIT ERROR] Failed to initialize LLM: {e}")
        return None


def call_llm_judge(
    llm: BaseChatModel,
    case: dict,
    payload: dict[str, Any]
) -> tuple[bool, list[str]]:
    question = case["question"]
    answer = (payload.get("answer") or "").strip()
    chunks = payload.get("chunks", []) or []
    context = "\n\n".join(chunks).strip()
    description = case.get("description", "").strip()

    GENERAL_KNOWLEDGE_DISCLAIMER = "This is based on general knowledge, not specific course material."
    MISSING_INFO_RESPONSE = "This information is not available in the specific course material."

    # Deterministic fast-path for exact missing-info response
    if answer == MISSING_INFO_RESPONSE:
        return True, []
    
    prompt = f"""
        You are a strict answer quality judge.

        Your task is to evaluate whether the assistant's ANSWER correctly follows the required decision policy.

        Return ONLY valid JSON with this exact schema:
        {{"passed": true, "notes": []}}
        or
        {{"passed": false, "notes": ["specific violation 1", "specific violation 2"]}}

        No markdown. No prose. No extra keys.

        ---

        ## ASSISTANT POLICY

        The assistant follows this exact decision order:

        PATH A — Metadata answers the question
        - If course metadata answers the question, the assistant should answer from metadata.
        - No disclaimer.
        - No outside knowledge.

        PATH B — Retrieved course material is topically relevant
        - If retrieved material contains any content that is topically relevant to the question, the assistant should answer from that material only.
        - No disclaimer.
        - No outside knowledge.
        - The answer may summarize, combine, or lightly infer from the retrieved material if the inference is straightforward and directly supported.

        PATH C — Missing course-specific fact
        - If the question asks for a course-specific fact or role-specific fact tied to the provided material
        (for example: exam room, due date, salary for this internship, grading rule, instructor policy,
        textbook used, office hour detail, location, logistics), and that fact is absent from metadata and retrieved material:
        the assistant should respond only with:
        "{MISSING_INFO_RESPONSE}"
        - No guessing.
        - No advice.
        - No disclaimer.

        PATH D — General/conceptual fallback
        - If the question is general or conceptual and metadata/retrieved material contain no relevant content,
        the assistant should begin with exactly:
        "{GENERAL_KNOWLEDGE_DISCLAIMER}"
        - Then it may answer using general knowledge.

        ---

        ## HOW TO CHOOSE THE CORRECT PATH

        Use this order:

        1. PATH A if metadata clearly answers the question.
        2. Otherwise PATH B if retrieved material contains any topically relevant content.
        3. Otherwise PATH C if the question asks for a missing course-specific or role-specific fact tied to the provided material.
        4. Otherwise PATH D.

        Important:
        - Prefer PATH A over PATH B when metadata clearly answers the question.
        - Prefer PATH B over PATH D whenever retrieved material discusses the same subject as the question, even partially.
        - Do NOT choose PATH C if the material actually contains the answer.
        - Do NOT choose PATH D if the material is topically relevant.

        ---

        ## EVALUATION RULES

        RULE 1 — Correct path selection
        Determine which path SHOULD have been used, then evaluate whether the answer matches that path.

        RULE 2 — PATH A / PATH B grounded-answer rules
        If the correct path is A or B:
        - FAIL if the answer includes "{GENERAL_KNOWLEDGE_DISCLAIMER}"
        - FAIL if the answer says the information is unavailable when the material clearly provides it
        - FAIL if the answer adds factual claims not supported by metadata/retrieved material
        - PASS if the answer is a correct concise restatement, aggregation, extraction, or directly supported summary

        Important clarification:
        - Do NOT fail merely because the answer is more concise than the source.
        - Do NOT fail merely because the answer combines facts from multiple retrieved chunks.
        - Do NOT fail for light paraphrasing or direct supported summarization.

        RULE 3 — PATH C missing-fact rules
        If the correct path is C:
        - PASS only if the answer is exactly:
        "{MISSING_INFO_RESPONSE}"
        - FAIL if the answer guesses, fabricates, or supplies a missing specific fact
        - FAIL if the answer gives advice like checking elsewhere, contacting someone, or looking in another document
        - FAIL if the answer includes "{GENERAL_KNOWLEDGE_DISCLAIMER}"

        RULE 4 — PATH D fallback rules
        If the correct path is D:
        - FAIL if the answer does not begin with exactly "{GENERAL_KNOWLEDGE_DISCLAIMER}"
        - FAIL if the answer contradicts the provided material
        - FAIL if the answer pretends the information came from course material

        RULE 5 — Fabrication
        Regardless of path:
        - FAIL if the answer includes specific facts not supported by metadata/retrieved material when the path is A or B
        - FAIL if the answer invents missing specific facts when the path is C
        - For PATH D, outside knowledge is allowed, but the answer must still be reasonable and not contradict the provided material

        RULE 6 — Relevance
        FAIL if the answer does not actually answer the question asked.

        RULE 7 — Clean output
        FAIL if the answer mentions:
        - chunk IDs
        - file names
        - metadata
        - retrieved materials
        - retrieval process

        ---

        ## IMPORTANT EDGE CASES

        Edge case 1:
        If the answer is correct but starts with "{GENERAL_KNOWLEDGE_DISCLAIMER}" even though the material clearly supports the answer,
        that is a failure.

        Edge case 2:
        If the material contains the subject but not the specific missing fact (for example salary, textbook, exam room),
        that is PATH C, not PATH B.

        Edge case 3:
        If the answer correctly lists multiple supported items from the retrieved material,
        that is valid and should not be treated as fabrication.

        Edge case 4:
        Do not mark something as a violation just because a rule section is "not applicable."

        ---

        ## INPUTS

        QUESTION:
        {question}

        TEST DESCRIPTION:
        {description}

        RETRIEVED MATERIAL:
        {context}

        ANSWER:
        {answer}

        ---

        ## FINAL CHECK

        Before producing JSON:
        - Choose exactly one correct path: A, B, C, or D.
        - Only include notes for real violations.
        - If there are no real violations, return passed=true and notes=[].

        Respond with JSON only.
        """

    raw = llm.invoke(prompt)
    text = raw if isinstance(raw, str) else raw.content

    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text.strip())

    try:
        data = json.loads(text)
        passed = bool(data.get("passed", False))
        notes = data.get("notes", [])
        if not isinstance(notes, list):
            notes = ["LLM judge returned invalid notes field"]
            passed = False
        return passed, [str(note) for note in notes]
    except Exception:
        return False, [f"LLM judge returned invalid JSON: {text[:200]}"]

