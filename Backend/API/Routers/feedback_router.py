from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import List, Dict, Any, Optional 
from API.Service.feedback_service import FeedbackService
from API.dependencies import get_feedback_service
from Metrics.metrics import MetricsRoute
from pydantic import BaseModel

router = APIRouter(prefix="/feedback", tags=["Feedbacks"], route_class=MetricsRoute)

# We keep the Request model for the POST body as it's standard for validation
class FeedbackRequest(BaseModel):
    course_id: str
    feedback_text: str

@router.post(
    "/submit",
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback for a course",
    description="Allows a student to submit feedback for a given course."
)
def submit_feedback(
    request: FeedbackRequest,
    service: FeedbackService = Depends(get_feedback_service),
) -> Dict[str, str]:
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
    "",
    status_code=status.HTTP_200_OK,
    summary="List all feedback",
    description="Retrieve all student feedback with optional pagination."
)
def get_all_feedback(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: FeedbackService = Depends(get_feedback_service),
):
    """Returns a dictionary containing 'total' and 'feedback' list."""
    try:
        return service.get_all_feedback(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve feedback: {str(e)}"
        )

@router.get(
    "/course/{course_id}",
    status_code=status.HTTP_200_OK,
    summary="Get feedback by course ID",
    description="Retrieve a paginated list of student feedback for a specific course."
)
def get_course_feedback(
    course_id: str = Path(..., description="The UUID of the course"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: FeedbackService = Depends(get_feedback_service),
):
    """Returns feedback for a specific course ID."""
    try:
        return service.get_course_feedback(course_id=course_id, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve course feedback: {str(e)}"
        )