from concurrent.futures import ThreadPoolExecutor, as_completed, as_completed
from threading import Lock
import time
from typing import Any

import requests
from langchain_core.language_models import BaseChatModel

from questions import QUESTIONS, ValidationQuestion
from utils import call_llm_judge, call_query_endpoint, get_llm, normalize, save_json


NO_ANSWER_TEXT = "I do not have enough course information to answer that."
print_lock = Lock()


class ValidationResultBase(ValidationQuestion):
    request_failed: bool

class ValidationResult(ValidationResultBase):
    rag_strategy: str
    answer: str
    sources: list[str]
    chunks: list[str]
    latency_ms: int

    passed_exact: bool
    passed_must_include: bool
    passed_must_not_include: bool
    passed_sources: bool
    passed_llm: bool
    passed_overall: bool
    notes: list[str]


def judge_response(case: ValidationQuestion, payload: dict[str, Any], latency_ms: int, llm: BaseChatModel) -> ValidationResult:
    result: ValidationResult = {
        **case,
        "request_failed": False,
        "rag_strategy": payload.get("strategy", ""),
        "answer": payload.get("answer", ""),
        "sources": payload.get("sources", []),
        "chunks": payload.get("chunks", []),
        "latency_ms": latency_ms,
        "passed_exact": True,
        "passed_must_include": True,
        "passed_must_not_include": True,
        "passed_sources": True,
        "passed_llm": True,
        "passed_overall": True,
        "notes": [],
    }

    expected_exact = case.get("expected_exact")
    if expected_exact is not None:
        result["passed_exact"] = normalize(result["answer"]) == normalize(expected_exact)
        if not result["passed_exact"]:
            result["notes"].append("Exact answer mismatch.")

    must_include = case.get("must_include", [])
    for phrase in must_include:
        if normalize(phrase) not in normalize(result["answer"]):
            result["passed_must_include"] = False
            result["notes"].append(f"Missing expected phrase: {phrase}")

    must_not_include = case.get("must_not_include", [])
    for phrase in must_not_include:
        if normalize(phrase) in normalize(result["answer"]):
            result["passed_must_not_include"] = False
            result["notes"].append(f"Forbidden phrase present: {phrase}")

    expected_sources = case.get("expected_sources", [])
    if expected_sources:
        normalized_actual_sources = {normalize(s) for s in result["sources"]}
        normalized_expected_sources = {normalize(s) for s in expected_sources}

        if not normalized_expected_sources.issubset(normalized_actual_sources):
            result["passed_sources"] = False
            result["notes"].append(
                f"Expected sources {expected_sources} not fully present in {result['sources']}"
            )

    passed_llm, llm_notes = call_llm_judge(llm, case, payload)
    result["passed_llm"] = passed_llm
    result["notes"].extend(llm_notes)

    result["passed_overall"] = all(
        [
            result["passed_exact"],
            result["passed_must_include"],
            result["passed_must_not_include"],
            result["passed_sources"],
            result["passed_llm"],
        ]
    )

    with print_lock: 
        status = "PASS" if result["passed_overall"] else "FAIL"
        print(f"\n[{status}] {result['id']}")
        print(f"Question: {result['question']}")
        print(f"Latency: {result['latency_ms']} ms")
        print(f"Sources: {result['sources']}")
        print(f"Answer: {result['answer']}")
        if result["notes"]:
            print("Notes:")
            for note in result["notes"]:
                print(f"  - {note}")
        print("\n" * 3)

        return result


def print_summary(results: list[ValidationResultBase]) -> None:
    total = len(results)
    passed = sum(r.get("passed_overall", 0) for r in results)
    failed_requests = sum(r["request_failed"] for r in results)

    print("\nSummary:")
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Request Failed: {failed_requests}")
    print(f"Success Rate: {(passed / total * 100):.2f}%")


def run_case(case: ValidationQuestion, llm: BaseChatModel) -> ValidationResultBase:
    try:
        latency_ms, payload = call_query_endpoint(course_id=case["course_id"], question=case["question"])
        result = judge_response(case, payload, latency_ms, llm)
    except requests.RequestException as e:
        result: ValidationResultBase = {
            **case,
            "request_failed": True,
            "notes": [f"Request failed: {e}"],
        }
    return result

def main(worker: int = 4) -> None:
    llm = get_llm()
    results: list[ValidationResult] = []

    with ThreadPoolExecutor(max_workers=worker) as executor:
        futures = [executor.submit(run_case, case, llm) for case in QUESTIONS]

        for future in as_completed(futures):
            results.append(future.result())

    save_json(f"validate_rag_result_{int(time.time())}.json", {"results": results})
    print_summary(results)


if __name__ == "__main__":
    main()