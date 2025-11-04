from fastapi import APIRouter, Depends, status, Path, Query, HTTPException
from API.Service.rag_service import RAGService
from API.dependencies import get_rag_service
from API.Service.students_service import StudentService
from API.dependencies import get_student_service
from typing import List, Dict

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

    # return rag_service.query(course_id, question)

    try:
        answer = rag_service.llm.invoke(question)
        return {"answer": answer, "sources": []}
    except Exception as e:
        return {"error": str(e), "sources": []}

# ------------------------------------------------------
# Get All Queries by Student
# ------------------------------------------------------
@router.get(
    "/courses/{course_id}/{student_id}/queries",
    summary="Get all queries from a specific student in a specific course",
    description="Fetches a list of all queries (with responses) made by a given student in a specific course."
)
def get_student_queries(
    course_id: str = Path(..., description="Course ID."),
    student_id: str = Path(..., description="Student's unique ID."),
    service: StudentService = Depends(get_student_service)
) -> Dict[str, List[Dict[str, str]]]:
    try:
        queries = service.sql_repo.read_queries_by_student(student_id, course_id)
        return {"queries": queries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve queries: {e}")
    
# ------------------------------------------------------
# Log a Student Query
# ------------------------------------------------------
@router.post(
    "students/log_query", 
    summary="Log a query made by a student",
    description="Stores a student's question and the corresponding system response."
)
def log_query(
    student_id: str = Query(..., description="Student's unique ID."),
    course_id: str = Query(..., description="Course ID related to the query."),
    query_text: str = Query(..., description="Text of the student's question."),
    response_text: str = Query(..., description="System's response text."),
    service: StudentService = Depends(get_student_service)
) -> Dict[str, str]:
    try:
        query_id = service.sql_repo.create_query_log(student_id, course_id, query_text, response_text)
        return {"message": "Query logged successfully", "query_id": query_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logging failed: {e}")