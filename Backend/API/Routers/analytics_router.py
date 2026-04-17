from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, status

from API.Service.analytics_service import AnalyticsService
from API.dependencies import (
    authorize_instructor,
    get_analytics_service,
    validate_course,
)
from Metrics.metrics import MetricsRoute


router = APIRouter(tags=["Analytics"], route_class=MetricsRoute)


@router.get(
    "/courses/{course_id}/analytics/overview",
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
    return service.get_course_overview(course_id=course_id, days=days)


@router.get(
    "/courses/{course_id}/analytics/top-questions",
    status_code=status.HTTP_200_OK,
    summary="Most frequently asked questions",
)
def get_top_questions(
    course_id: str = Path(...),
    limit: int = Query(10, ge=1, le=100),
    days: Optional[int] = Query(
        None,
        description="Optional time window in days (e.g., 7, 30, 90).",
    ),
    _course: dict = Depends(validate_course),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_top_questions(course_id=course_id, limit=limit, days=days)


@router.get(
    "/courses/{course_id}/analytics/top-keywords",
    status_code=status.HTTP_200_OK,
    summary="Most searched keywords",
)
def get_top_keywords(
    course_id: str = Path(...),
    limit: int = Query(20, ge=1, le=100),
    days: Optional[int] = Query(
        None,
        description="Optional time window in days (e.g., 7, 30, 90).",
    ),
    _course: dict = Depends(validate_course),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_top_keywords(course_id=course_id, limit=limit, days=days)


@router.get(
    "/courses/{course_id}/analytics/engagement",
    status_code=status.HTTP_200_OK,
    summary="Student engagement metrics",
)
def get_engagement(
    course_id: str = Path(...),
    _course: dict = Depends(validate_course),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_engagement_metrics(course_id=course_id)


@router.get(
    "/courses/{course_id}/analytics/usage-trend",
    status_code=status.HTTP_200_OK,
    summary="Course usage trend over time",
)
def get_course_usage_trend(
    course_id: str = Path(...),
    days: int = Query(7, ge=1, le=365),
    _course: dict = Depends(validate_course),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_course_usage_trend(course_id=course_id, days=days)


@router.get(
    "/instructors/{instructor_id}/analytics/query-distribution",
    status_code=status.HTTP_200_OK,
    summary="Query distribution across an instructor's courses",
)
def get_instructor_query_distribution(
    instructor_id: str = Path(...),
    days: Optional[int] = Query(None, ge=1, le=365),
    _auth: dict = Depends(authorize_instructor),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_instructor_query_distribution(instructor_id=instructor_id, days=days)


@router.get(
    "/instructors/{instructor_id}/analytics/system-overview",
    status_code=status.HTTP_200_OK,
    summary="System-wide analytics overview",
)
def get_system_overview(
    instructor_id: str = Path(...),
    _auth: dict = Depends(authorize_instructor),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_system_overview()


@router.get(
    "/instructors/{instructor_id}/analytics/system-query-trend",
    status_code=status.HTTP_200_OK,
    summary="System-wide query trend",
)
def get_system_query_trend(
    instructor_id: str = Path(...),
    days: int = Query(30, ge=1, le=365),
    _auth: dict = Depends(authorize_instructor),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_system_query_trend(days=days)


@router.get(
    "/instructors/{instructor_id}/analytics/documents-by-course",
    status_code=status.HTTP_200_OK,
    summary="Documents uploaded per course",
)
def get_documents_by_course(
    instructor_id: str = Path(...),
    _auth: dict = Depends(authorize_instructor),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_documents_per_course()


@router.get(
    "/instructors/{instructor_id}/analytics/documents-by-instructor",
    status_code=status.HTTP_200_OK,
    summary="Documents uploaded per instructor",
)
def get_documents_by_instructor(
    instructor_id: str = Path(...),
    _auth: dict = Depends(authorize_instructor),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_documents_per_instructor()


@router.get(
    "/instructors/{instructor_id}/analytics/courses-by-instructor",
    status_code=status.HTTP_200_OK,
    summary="Courses created per instructor",
)
def get_courses_by_instructor(
    instructor_id: str = Path(...),
    _auth: dict = Depends(authorize_instructor),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_courses_per_instructor()


@router.get(
    "/instructors/{instructor_id}/analytics/queries-by-course",
    status_code=status.HTTP_200_OK,
    summary="System-wide AI query volume per course",
)
def get_queries_by_course(
    instructor_id: str = Path(...),
    days: Optional[int] = Query(None, ge=1, le=365),
    _auth: dict = Depends(authorize_instructor),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_queries_per_course(days=days)
