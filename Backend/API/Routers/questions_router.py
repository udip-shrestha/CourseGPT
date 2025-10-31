from fastapi import APIRouter, Depends, status, Path, Query
from API.Service.rag_service import RAGService
from API.dependencies import get_rag_service

router = APIRouter(tags=["Questions"])


@router.post(
    "/courses/{course_id}/queries",
    status_code=status.HTTP_200_OK,
    summary="Ask a question about a course",
    description=(
        "**Action:** Runs the full RAG pipeline to answer a user's question based on "
        "documents previously uploaded for the specified course.\n\n"
        "**Returns:** A JSON object containing the generated answer and document sources."
    ),
)
def ask_question(
    course_id: str = Path(
        ...,
        description="UUID of the course to query (e.g., 'data-structures-2025').",
    ),
    question: str = Query(
        ...,
        description="The question to ask about the course materials.",
        example="What is polymorphism in object-oriented programming?",
    ),
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    **Pipeline:** Retriever → Prompt → LLM  
    Uses stored course documents to generate an answer with sources.
    """
    if not question.strip():
        return {"answer": "Question cannot be empty.", "sources": ""}

    return rag_service.query(course_id, question)
