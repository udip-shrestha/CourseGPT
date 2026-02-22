from typing import Optional

from API.Repository.i_sql_repository import ISQLRepository
from API.Util.decorators import clean_service


class FeedbackService:
    """
    Handles creation, retrieval, listing, and deletion of feedback.
    Interacts with the SQL repository to manage persistent feedback data.
    """

    def __init__(self, sql_repo: ISQLRepository):
        self.sql_repo = sql_repo

    # ------------------------------------------------------
    # Create Feedback
    # ------------------------------------------------------
    @clean_service
    def create_feedback(self, course_id: str, feedback_text: str, received_at: Optional[str] = None) -> dict:
        """
        Persist a feedback record for a course.
        Returns a dict containing the new feedback id.
        """
        fid = self.sql_repo.create_feedback(course_id=course_id, feedback_text=feedback_text, received_at=received_at)
        return {"feedback_id": fid}
