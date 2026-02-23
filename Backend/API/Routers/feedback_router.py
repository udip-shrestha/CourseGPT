from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import List, Dict, Any, Optional 
from API.Service.feedback_service import FeedbackService
from API.dependencies import get_feedback_service
from Metrics.metrics import MetricsRoute
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


router = APIRouter(prefix="/feedback", tags=["Feedbacks"], route_class=MetricsRoute)

class FeedbackRequest(BaseModel):
    course_id: str
    feedback_text: str

class FeedbackResponse(BaseModel):
    feedback_id: str
    message: str
class FeedbackItem(BaseModel):
    id: UUID
    course_id: UUID
    course_name: Optional[str] = None # Only populated in /all
    feedback_text: str
    received_at: datetime

class FeedbackListResponse(BaseModel):
    total: int
    feedback: List[FeedbackItem]


@router.post(
    "/submit",
    status_code=status.HTTP_201_CREATED,
    response_model=FeedbackResponse,
    summary="Submit feedback for a course",
    description="Allows a student to submit feedback for a given course."
)
def submit_feedback(
    request: FeedbackRequest,
    service: FeedbackService = Depends(get_feedback_service),
):
    """Accepts and persists feedback for a course."""
    try:
        res = service.create_feedback(
            course_id=request.course_id, 
            feedback_text=request.feedback_text
        )
        return {
            "feedback_id": res.get("feedback_id"), 
            "message": "Feedback received. Thanks for your input!"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to save feedback: {str(e)}"
        )

@router.get(
    "/all",
    response_model=FeedbackListResponse,
    summary="Get all feedback",
    description="Returns a paginated list of all feedback in the system. Typically used by admins."
)
def get_all_feedback(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: FeedbackService = Depends(get_feedback_service),
):
    try:
        return service.get_all_feedback(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve feedback: {str(e)}"
        )

@router.get(
    "/course/{course_id}",
    response_model=FeedbackListResponse,
    summary="Get feedback per course",
    description="Returns a paginated list of feedback for a specific course ID."
)
def get_course_feedback(
    course_id: str = Path(..., description="The UUID of the course"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: FeedbackService = Depends(get_feedback_service),
):
    try:
        return service.get_course_feedback(course_id=course_id, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve course feedback: {str(e)}"
        )