from fastapi import APIRouter, Query, Depends, HTTPException, status
from typing import Dict
from API.Service.feedback_service import FeedbackService
from API.dependencies import get_feedback_service
from Metrics.metrics import MetricsRoute
from pydantic import BaseModel

router = APIRouter(prefix="/feedback", tags=["Feedbacks"], route_class=MetricsRoute)

class FeedbackRequest(BaseModel):
    course_id: str
    feedback_text: str

class FeedbackResponse(BaseModel):
    feedback_id: str
    message: str

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
) -> Dict[str, str]:
    """Accepts and persists feedback for a course."""
    try:
        res = service.create_feedback(course_id=request.course_id, feedback_text=request.feedback_text)
        return {"feedback_id": res.get("feedback_id"), "message": "Feedback received. Thanks for your input!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {e}")
