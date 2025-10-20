from fastapi import HTTPException, status
from typing import List, Optional

from API.Repository.i_sql_repository import ISQLRepository
from API.Util.decorators import clean_service


class CourseService:
    """
    Handles creation, retrieval, listing, and deletion of courses.
    Interacts with the SQL repository to manage persistent course data.
    """

    def __init__(
        self,
        sql_repo: ISQLRepository
    ):
        self.sql_repo = sql_repo

    # ------------------------------------------------------
    # Create Course
    # ------------------------------------------------------
    @clean_service
    def create_course(
        self,
        instructor_id: str,
        name: str,
        institution: str,
        semester_id: int,
        year: int
    ) -> dict:
        """
        1️⃣ Validate that instructor exists.
        2️⃣ Persist new course record in the database.
        """
        instructor = self.sql_repo.read_instructor(instructor_id)
        if not instructor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instructor with id={instructor_id} not found."
            )

        course_id = self.sql_repo.create_course(
            instructor_id=instructor_id,
            name=name,
            institution=institution,
            semester_id=semester_id,
            year=year
        )

        return {"course_id": course_id}

    # ------------------------------------------------------
    # Read Single Course
    # ------------------------------------------------------
    @clean_service
    def read_course(self, course_id: str) -> dict:
        """Fetch one course by its unique ID."""
        course = self.sql_repo.read_course(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with id={course_id} not found."
            )
        return course

    # ------------------------------------------------------
    # Read All Courses
    # ------------------------------------------------------
    @clean_service
    def read_all_courses(
        self,
        instructor_id: Optional[str] = None,
        institution: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "created_at",
        order_dir: str = "desc"
    ) -> List[dict]:
        """
        Fetch all courses with optional filters and pagination.
        Allows filtering by instructor or institution name.
        """
        return self.sql_repo.read_all_courses(
            instructor_id=instructor_id,
            institution=institution,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_dir=order_dir
        )

    # ------------------------------------------------------
    # Delete Course
    # ------------------------------------------------------
    @clean_service
    def delete_course(self, course_id: str):
        """
        Remove a course record permanently from the system.
        """
        course = self.sql_repo.read_course(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with id={course_id} not found."
            )

        self.sql_repo.delete_course(course_id)
        return {"status": "deleted", "course_id": course_id}
