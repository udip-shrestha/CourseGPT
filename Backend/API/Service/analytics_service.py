from typing import Optional
from fastapi import HTTPException, status
from API.Repository.i_sql_repository import ISQLRepository
from API.Util.decorators import clean_service


class AnalyticsService:
    """
    Read-only analytics aggregation layer.

    Responsibilities:
      • Aggregating query + student metrics
      • Normalizing data for dashboards
      • Delegating heavy aggregation to SQL repo
    """

    def __init__(self, sql_repo: ISQLRepository):
        self.sql_repo = sql_repo

    # ------------------------------------------------------
    # Overview metrics
    # ------------------------------------------------------
    @clean_service
    def get_course_overview(self, course_id: str, days: Optional[int] = None) -> dict:
        stats = self.sql_repo.read_course_query_stats(course_id, days)

        if stats is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No analytics found for course={course_id}"
            )

        return stats

    # ------------------------------------------------------
    # Top repeated questions
    # ------------------------------------------------------
    @clean_service
    def get_top_questions(self, course_id: str, limit: int = 10, days: Optional[int] = None) -> dict:
        return self.sql_repo.read_top_questions(course_id, limit, days)
    
    # ------------------------------------------------------
    # Keyword frequency
    # ------------------------------------------------------
    @clean_service
    def get_top_keywords(self, course_id: str, limit: int = 20, days: Optional[int] = None) -> dict:
        return self.sql_repo.read_top_keywords(course_id, limit, days)

    # ------------------------------------------------------
    # Engagement metrics
    # ------------------------------------------------------
    @clean_service
    def get_engagement_metrics(self, course_id: str) -> dict:
        return self.sql_repo.read_engagement_stats(course_id)

    # ------------------------------------------------------
    # Course usage trend
    # ------------------------------------------------------
    @clean_service
    def get_course_usage_trend(self, course_id: str, days: int = 7) -> list[dict]:
        return self.sql_repo.read_course_usage_trend(course_id, days)

    # ------------------------------------------------------
    # Instructor query distribution
    # ------------------------------------------------------
    @clean_service
    def get_instructor_query_distribution(
        self, instructor_id: str, days: Optional[int] = None
    ) -> list[dict]:
        return self.sql_repo.read_instructor_query_distribution(instructor_id, days)

    # ------------------------------------------------------
    # System overview
    # ------------------------------------------------------
    @clean_service
    def get_system_overview(self) -> dict:
        return self.sql_repo.read_system_overview()

    # ------------------------------------------------------
    # System query trend
    # ------------------------------------------------------
    @clean_service
    def get_system_query_trend(self, days: int = 30) -> list[dict]:
        return self.sql_repo.read_system_query_trend(days)

    # ------------------------------------------------------
    # System chart data
    # ------------------------------------------------------
    @clean_service
    def get_documents_per_course(self) -> list[dict]:
        return self.sql_repo.read_documents_per_course()

    @clean_service
    def get_documents_per_instructor(self) -> list[dict]:
        return self.sql_repo.read_documents_per_instructor()

    @clean_service
    def get_courses_per_instructor(self) -> list[dict]:
        return self.sql_repo.read_courses_per_instructor()

    @clean_service
    def get_queries_per_course(self, days: Optional[int] = None) -> list[dict]:
        return self.sql_repo.read_queries_per_course(days)
