import re
from typing import List, Tuple
from langchain_core.documents import Document


def clean_and_format_response(
    text: str,
    source_documents: List[Document]
) -> Tuple[str, str]:
    """
    Cleans and formats a conversational LLM response for readability and consistency.

    1️⃣ Remove leftover prompt context (e.g., "Context:" / "Answer:").
    2️⃣ Normalize spacing and punctuation.
    3️⃣ Aggregate and format document sources.

    Args:
        text: Raw LLM output (string).
        source_documents: Documents used for retrieval context.
        min_length: Minimum reasonable response length before padding.
        max_length: Maximum response length before truncation.

    Returns:
        Tuple[str, str]: (clean_answer, formatted_sources)
    """

    # --- Step 1: Remove common prompt artifacts ---
    clean_text = re.sub(r"(?is)\b(?:context|question|answer)\s*[:\-]+\s*","",text or "",).strip()
    
    # --- Step 2: Ensure ending punctuation ---
    clean_text = re.sub(r"\s+", " ", clean_text).strip()
    if clean_text and clean_text[-1] not in ".!?":
        clean_text += "."

    # --- Step 3: Build formatted source string ---
    unique_sources = set()
    for doc in source_documents or []:
        source = doc.metadata.get("source") or doc.metadata.get("file_name") or "Unknown"
        page = doc.metadata.get("page")
        entry = f"{source} (page {page})" if page else source
        unique_sources.add(entry)
    sources_str = "; ".join(sorted(unique_sources)) if unique_sources else "No sources found"

    return clean_text.strip(), sources_str

