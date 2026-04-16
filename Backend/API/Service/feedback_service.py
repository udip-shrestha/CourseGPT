from fastapi import HTTPException, status
from psycopg.errors import UniqueViolation
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

    @clean_service
    def submit_vote(self, course_id: str, student_id: str, query_id: str, vote: str) -> dict:
        """Persist an up/down vote for a generated answer."""
        if vote not in ("up", "down"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid vote")

        try:
            vote_id = self.sql_repo.create_answer_feedback(
                course_id=course_id,
                student_id=student_id,
                query_id=query_id,
                vote=vote,
            )
            return {"vote_id": vote_id}
        except UniqueViolation:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already voted")

    @clean_service
    def get_course_satisfaction(self, course_id: str) -> dict:
        """Return course satisfaction metrics based on student vote feedback."""
        return self.sql_repo.read_course_satisfaction(course_id=course_id)

    @clean_service
    def get_all_feedback(self, limit: int = 50, offset: int = 0) -> dict:
        """Retrieve all feedback from all courses."""
        return self.sql_repo.read_all_feedback(limit=limit, offset=offset)

    @clean_service
    def get_course_feedback(self, course_id: str, limit: int = 50, offset: int = 0) -> dict:
        """Retrieve feedback specifically for one course."""
        return self.sql_repo.read_all_feedback_for_course(course_id=course_id, limit=limit, offset=offset)
