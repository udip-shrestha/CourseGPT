from fastapi import APIRouter, Depends, Path, Query, status
from typing import Optional
from API.Service.analytics_service import AnalyticsService
from API.dependencies import get_analytics_service, validate_course
from Metrics.metrics import MetricsRoute

router = APIRouter(
    prefix="/courses/{course_id}/analytics",
    tags=["Analytics"],
    route_class=MetricsRoute,
)


@router.get(
    "/overview",
    status_code=status.HTTP_200_OK,
    summary="Course analytics overview",
)
def get_overview(
    course_id: str = Path(...),
    days: Optional[int] = Query(
        None,
        description="Optional time window in days (e.g., last 7 days).",
    ),
    _course: dict = Depends(validate_course),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Returns high-level metrics:
      • total queries
      • unique active students
      • avg queries per student
      • queries per day
    """
    return service.get_course_overview(course_id=course_id, days=days)


@router.get(
    "/top-questions",
    status_code=status.HTTP_200_OK,
    summary="Most frequently asked questions",
)
def get_top_questions(
    course_id: str = Path(...),
    limit: int = Query(10, ge=1, le=100),
    _course: dict = Depends(validate_course),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Returns most repeated or similar questions.
    """
    return service.get_top_questions(course_id=course_id, limit=limit)


@router.get(
    "/top-keywords",
    status_code=status.HTTP_200_OK,
    summary="Most searched keywords",
)
def get_top_keywords(
    course_id: str = Path(...),
    limit: int = Query(20, ge=1, le=100),
    _course: dict = Depends(validate_course),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Extracts and ranks common keywords from student questions.
    """
    return service.get_top_keywords(course_id=course_id, limit=limit)


@router.get(
    "/engagement",
    status_code=status.HTTP_200_OK,
    summary="Student engagement metrics",
)
def get_engagement(
    course_id: str = Path(...),
    _course: dict = Depends(validate_course),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Returns engagement stats:
      • total students
      • active students
      • queries per student distribution
      • Discord-linked usage stats
    """
    return service.get_engagement_metrics(course_id=course_id)
