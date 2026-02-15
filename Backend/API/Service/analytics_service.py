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
    def get_top_questions(self, course_id: str, limit: int = 10) -> dict:
        return self.sql_repo.read_top_questions(course_id, limit)

    # ------------------------------------------------------
    # Keyword frequency
    # ------------------------------------------------------
    @clean_service
    def get_top_keywords(self, course_id: str, limit: int = 20) -> dict:
        return self.sql_repo.read_top_keywords(course_id, limit)

    # ------------------------------------------------------
    # Engagement metrics
    # ------------------------------------------------------
    @clean_service
    def get_engagement_metrics(self, course_id: str) -> dict:
        return self.sql_repo.read_engagement_stats(course_id)
