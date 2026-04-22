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
        discord_id: str | None,
        course_id: str,
        canvas_user_id: str | None = None,
    ) -> dict:
        """
        Create or update a student record in the database.

        Either discord_id or canvas_user_id should be provided (or both). The repository
        handles merging duplicates and linking to the course.
        """

        student_id = self.sql_repo.create_student(
            name=name,
            discord_id=discord_id,
            course_id=course_id,
            canvas_user_id=canvas_user_id,
        )

        return {"student_id": student_id}

    # ------------------------------------------------------
    # Canvas helpers
    # ------------------------------------------------------
    @clean_service
    def find_student_in_course_by_canvas(
        self,
        canvas_user_id: str,
        course_id: str,
    ) -> dict | None:
        """Return student record if user exists and is enrolled in the course."""
        student = self.sql_repo.read_student_by_canvas(canvas_user_id)
        if not student:
            return None
        # verify enrollment
        students = self.sql_repo.read_all_students(course_id=course_id)
        for s in students:
            if s.get("id") == student.get("id"):
                return student
        return None

    @clean_service
    def register_canvas_student(
        self,
        name: str,
        canvas_user_id: str,
        course_id: str,
    ) -> dict:
        """Create a student using their Canvas user id and link to the course."""
        student_id = self.sql_repo.create_student(
            name=name,
            discord_id=None,
            course_id=course_id,
            canvas_user_id=canvas_user_id,
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

        if limit is None:
            return students
        # simple pagination (repository could also handle it internally)
        paginated = students[offset:offset + limit]
        return paginated
    # ------------------------------------------------------
    # COUNT All Students
    # ------------------------------------------------------

    @clean_service
    def count_students(self, course_id: str) -> int:
        """Return total number of students in a course (no pagination)."""
        students = self.sql_repo.read_all_students(course_id=course_id)
        return len(students)

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