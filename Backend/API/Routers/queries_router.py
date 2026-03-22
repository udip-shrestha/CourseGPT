from fastapi import APIRouter, Depends, WebSocket, status, Path, Query
from typing import Optional
from API.Service.queries_service import QueryService
from API.dependencies import get_query_service, validate_course, get_web_socket_manager
from API.Util.web_socket_manager import WebSocketManager
from Metrics.metrics import MetricsRoute


router = APIRouter(tags=["Queries"], route_class=MetricsRoute)


COURSE_QUERIES_WS_ROUTE = "/courses/{course_id}/queries"


@router.post(
    "/courses/{course_id}/queries",
    status_code=status.HTTP_200_OK,
    summary="Ask a new question about a course",
    description=(
        "**Action:** Executes the full RAG pipeline using stored course materials. "
        "The system retrieves relevant chunks, builds a grounded prompt, and returns the generated answer.\n\n"
        "**Returns:** JSON containing the generated answer, retrieved source chunks, "
        "and internal metadata (timestamps, IDs)."
    ),
)
def ask_question(
    course_id: str = Path(
        ...,
        description="UUID of the course the question belongs to.",
        examples={"example": "8b7e9f2a-d4a1-4e5c-94b9-3c6f4ab0e9cd"},
    ),
    question: str = Query(
        ...,
        description="The student's natural-language question.",
        examples={"example": "What is the difference between a controller and a service?"},
    ),
    student_id: Optional[str] = Query(
        None,
        description="Optional student UUID (used for author attribution and analytics).",
        examples={"example": "c3e82b9d-f24d-4b1e-9e5c-0affd12e90b3"},
    ),
    validate: bool = Query(
        False, 
        description="When true, include retrieval data for evaluation."
    ),
    course: dict = Depends(validate_course),
    service: QueryService = Depends(get_query_service),
    web_socket_manager: WebSocketManager = Depends(get_web_socket_manager),
):
    """Run the full RAG answer-generation pipeline for a single question."""

    # Step 1: run RAG + save in DB
    result = service.ask_question(course_id=course_id, course=course, question=question, validate=validate, student_id=student_id)

    # Step 2: broadcast event to websocket subscribers
    web_socket_manager.publish(COURSE_QUERIES_WS_ROUTE.format(course_id=course_id), {
        "event": "new_query",
        "question": question,
        "answer": result.get("answer", ""),
    })

    return result


@router.get(
    "/courses/{course_id}/queries",
    status_code=status.HTTP_200_OK,
    summary="List all queries for a course (with pagination)",
    description=(
        "**Action:** Retrieves a paginated list of all questions asked in the course. "
        "Supports ordering and pagination to efficiently navigate the query history.\n\n"
        "**Returns:** `{ total, queries: [...] }` including question text, answer, timestamps, and student metadata."
    ),
)
def get_course_queries(
    course_id: str = Path(
        ...,
        description="UUID of the course.",
        examples={"example": "8b7e9f2a-d4a1-4e5c-94b9-3c6f4ab0e9cd"},
    ),
    limit: int = Query(
        10,
        ge=1,
        description="Maximum number of results per page.",
        examples={"example": 10},
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Pagination offset (starting index).",
        examples={"example": 0},
    ),
    order_by: str = Query(
        "asked_at",
        description="Field to sort by: `asked_at`, `student_id`, or `question`.",
        examples={"example": "asked_at"},
    ),
    order_dir: str = Query(
        "desc",
        description="Sort direction.",
        examples={"example": "desc"},
        pattern="^(asc|desc)$",
    ),
    _course: dict = Depends(validate_course),
    service: QueryService = Depends(get_query_service),
):
    """Retrieve paginated Q/A history for an entire course."""
    return service.get_course_queries(
        course_id=course_id,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_dir=order_dir,
    )


@router.get(
    "/courses/{course_id}/students/{student_id}/queries",
    status_code=status.HTTP_200_OK,
    summary="List all queries for a specific student in a course",
    description=(
        "**Action:** Retrieves all questions asked by a specific student, with pagination and sorting.\n\n"
        "**Returns:** `{ total, queries: [...] }` including timestamps and answers."
    ),
)
def get_student_queries(
    course_id: str = Path(
        ...,
        description="UUID of the course.",
        examples={"example": "8b7e9f2a-d4a1-4e5c-94b9-3c6f4ab0e9cd"},
    ),
    student_id: str = Path(
        ...,
        description="UUID of the student.",
        examples={"example": "c3e82b9d-f24d-4b1e-9e5c-0affd12e90b3"},
    ),
    limit: int = Query(
        10,
        ge=1,
        description="Maximum results per page.",
        examples={"example": 10},
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of items to skip.",
        examples={"example": 0},
    ),
    order_by: str = Query(
        "asked_at",
        description="Field to sort by.",
        examples={"example": "asked_at"},
    ),
    order_dir: str = Query(
        "desc",
        description="Sort direction.",
        examples={"example": "desc"},
        pattern="^(asc|desc)$",
    ),
    _course: dict = Depends(validate_course),
    service: QueryService = Depends(get_query_service),
):
    """Fetch all Q/A history for a single student."""
    return service.get_student_queries(
        course_id=course_id,
        student_id=student_id,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_dir=order_dir,
    )


@router.get(
    "/courses/{course_id}/queries/{query_id}",
    status_code=status.HTTP_200_OK,
    summary="Retrieve a specific query by ID",
    description=(
        "**Action:** Fetch a single stored question/answer entry by its unique ID.\n\n"
        "**Returns:** The full record including question text, answer, sources, and timestamps."
    ),
)
def read_query(
    course_id: str = Path(
        ...,
        description="UUID of the course.",
        examples={"example": "8b7e9f2a-d4a1-4e5c-94b9-3c6f4ab0e9cd"},
    ),
    query_id: str = Path(
        ...,
        description="UUID of the query.",
        examples={"example": "fa0d35a3-7d23-4e2e-8f0b-f34f42a8832c"},
    ),
    _course: dict = Depends(validate_course),
    service: QueryService = Depends(get_query_service),
):
    """Fetch one stored question/answer by ID."""
    return service.get_query(course_id, query_id)


@router.delete(
    "/courses/{course_id}/queries/{query_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a stored query",
    description=(
        "**Action:** Permanently deletes a question/answer pair from the system.\n\n"
        "**Returns:** 204 No Content when successful."
    ),
)
def delete_query(
    course_id: str = Path(
        ...,
        description="UUID of the course.",
        examples={"example": "8b7e9f2a-d4a1-4e5c-94b9-3c6f4ab0e9cd"},
    ),
    query_id: str = Path(
        ...,
        description="UUID of the query to delete.",
        examples={"example": "fa0d35a3-7d23-4e2e-8f0b-f34f42a8832c"},
    ),
    _course: dict = Depends(validate_course),
    service: QueryService = Depends(get_query_service),
):
    """Delete a stored query entry."""
    return service.delete_query(course_id, query_id)


@router.websocket(COURSE_QUERIES_WS_ROUTE)
async def subscribe_to_course_queries(
    websocket: WebSocket,
    _course: dict = Depends(validate_course),
    manager: WebSocketManager = Depends(get_web_socket_manager),
):
    """
    WebSocket endpoint for subscribing to real-time query updates for a course.
    """
    await manager.handle_subscription(websocket.url.path, websocket)

