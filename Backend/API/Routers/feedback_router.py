from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import List, Dict, Any, Optional 
from API.Service.feedback_service import FeedbackService
from API.dependencies import get_feedback_service
from Metrics.metrics import MetricsRoute
from pydantic import BaseModel

router = APIRouter(prefix="/feedback", tags=["Feedbacks"], route_class=MetricsRoute)


class FeedbackRequest(BaseModel):
    course_id: str
    feedback_text: str

class VoteRequest(BaseModel):
    course_id: str
    student_id: str
    query_id: str
    vote: str

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

@router.post(
    "/vote",
    status_code=status.HTTP_201_CREATED,
    summary="Submit an answer vote for a generated query",
    description="Records a student's up/down vote for a generated course answer."
)
def submit_vote(
    request: VoteRequest,
    service: FeedbackService = Depends(get_feedback_service),
):
    if request.vote not in ("up", "down"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid vote")

    try:
        res = service.submit_vote(
            course_id=request.course_id,
            student_id=request.student_id,
            query_id=request.query_id,
            vote=request.vote,
        )
        return {
            "vote_id": res.get("vote_id"),
            "message": "Vote recorded"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record vote: {str(e)}"
        )

@router.get(
    "/courses/{course_id}/satisfaction",
    status_code=status.HTTP_200_OK,
    summary="Get course satisfaction based on answer votes",
    description="Returns aggregated satisfaction metrics for a course based on answer feedback votes."
)
def get_course_satisfaction(
    course_id: str = Path(..., description="The UUID of the course"),
    service: FeedbackService = Depends(get_feedback_service),
):
    try:
        return service.get_course_satisfaction(course_id=course_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve course satisfaction: {str(e)}"
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
    "/courses/{course_id}/answer-feedbacks",
    status_code=status.HTTP_200_OK,
    summary="Get answer feedbacks by course ID",
    description="Retrieve a paginated list of all answer feedbacks (votes) for a specific course."
)
def get_course_answer_feedbacks(
    course_id: str = Path(..., description="The UUID of the course"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: FeedbackService = Depends(get_feedback_service),
):
    """Returns all answer feedbacks (votes) for a specific course ID."""
    try:
        return service.get_course_answer_feedbacks(course_id=course_id, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve course answer feedbacks: {str(e)}"
        )
@router.get(
    "/courses/{course_id}",
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