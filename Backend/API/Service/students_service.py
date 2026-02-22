from fastapi import HTTPException, status
from typing import List, Optional

from API.Repository.i_sql_repository import ISQLRepository
from API.Util.decorators import clean_service


class StudentService:
    """
    Handles creation, retrieval, listing, and deletion of students.
    Interacts with the SQL repository to manage persistent student data.
    """

    def __init__(self, sql_repo: ISQLRepository):
        self.sql_repo = sql_repo

    # ------------------------------------------------------
    # Create Student
    # ------------------------------------------------------
    @clean_service
    def create_student(
        self,
        name: str,
        discord_id: str,
        course_id: str,
    ) -> dict:
        """
        Create a new student record in the database.
        """
        # Optional: check if a student with the same Discord ID already exists for this course
        # existing_students = self.sql_repo.read_all_students(course_id=course_id)
        # if any(s["discord_id"] == discord_id for s in existing_students):
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"Student with discord_id={discord_id} already exists in this course."
        #     )

        student_id = self.sql_repo.create_student(
            name=name,
            discord_id=discord_id,
            course_id=course_id
        )

        return {"student_id": student_id}

    # ------------------------------------------------------
    # Read Single Student
    # ------------------------------------------------------
    @clean_service
    def read_student(self, student_id: str) -> dict:
        """Fetch one student by its unique ID."""
        student = self.sql_repo.read_student(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with id={student_id} not found."
            )
        return student

    # ------------------------------------------------------
    # Read All Students
    # ------------------------------------------------------
    @clean_service
    def read_all_students(
        self,
        course_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[dict]:
        """Fetch all students with optional filtering by course_id."""
        students = self.sql_repo.read_all_students(course_id=course_id)

        # simple pagination (repository could also handle it internally)
        paginated = students[offset:offset + limit]
        return paginated

    # ------------------------------------------------------
    # Delete Student
    # ------------------------------------------------------
    @clean_service
    def delete_student(self, student_id: str) -> dict:
        """Remove a student record permanently from the database."""
        student = self.sql_repo.read_student(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with id={student_id} not found."
            )

        self.sql_repo.delete_student(student_id)
        return {"status": "deleted", "student_id": student_id}


    def unregister_student(self, discord_id: str, course_id: str) -> bool:
        """
        Removes a student-course mapping.
        Returns True if successful, False otherwise.
        """
        student = self.sql_repo.read_student_by_discord(discord_id)
        if not student:
            return False

        return self.sql_repo.remove_student_from_course(student["id"], course_id)