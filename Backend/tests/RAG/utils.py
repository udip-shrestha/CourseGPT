import json
import os
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

def call_llm_judge(llm: BaseChatModel, case: dict, payload: dict[str, Any]) -> tuple[bool, list[str]]:
    question = case["question"]
    answer = payload.get("answer", "")
    chunks = payload.get("chunks", []) or []
    context = "\n\n".join(chunks)
    prompt = f"""
    You are an answer quality judge. Evaluate the ANSWER to the QUESTION using only the RETRIEVED MATERIAL.

    Output ONLY a JSON object in this exact format with no text before or after:
    {{"passed": <true or false>, "notes": ["<reason if failed, else empty>"]}}

    ---

    EVALUATION RULES:

    **RULE 1 — NO ANSWER CASE (check this first):**
    If the RETRIEVED MATERIAL does not contain enough information to answer the QUESTION,
    the ANSWER must be EXACTLY: "I do not have enough course information to answer that."
    - If the material lacks the answer AND the ANSWER uses this exact sentence → passed=true, notes=[]
    - If the material lacks the answer BUT the ANSWER says something else → passed=false, explain why
    - If the material DOES contain the answer BUT the ANSWER uses this sentence → passed=false, explain why

    **RULE 2 — GROUNDING:**
    Every claim in the ANSWER must be supported by the RETRIEVED MATERIAL.
    If the ANSWER introduces facts not present in the material → passed=false, list the unsupported claims.

    **RULE 3 — RELEVANCE:**
    The ANSWER must address the QUESTION. If it answers a different question or goes off-topic → passed=false.

    **RULE 4 — NO HALLUCINATION:**
    The ANSWER must not contradict or fabricate details not in the RETRIEVED MATERIAL.

    **PASS CRITERIA:**
    passed=true only if ALL rules above are satisfied.
    passed=false if ANY rule is violated. List each violation in notes.
    Extra detail is acceptable as long as it is grounded in the material.

    ---

    QUESTION:
    {question}

    RETRIEVED MATERIAL:
    {context}

    ANSWER:
    {answer}
    """
    
    raw = llm.invoke(prompt)
    text = raw if isinstance(raw, str) else raw.content

    try:
        data = json.loads(text)
        return bool(data.get("passed", False)), list(data.get("notes", []))
    except Exception:
        return False, ["LLM judge returned invalid JSON"]
    
