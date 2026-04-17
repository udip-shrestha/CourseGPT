from fastapi import HTTPException, status
from typing import List, Optional

from API.Repository.i_sql_repository import ISQLRepository
from API.Repository.i_vector_repository import IVectorRepository
from API.Util.decorators import clean_service


class CourseService:
    """
    Handles creation, retrieval, listing, and deletion of courses.
    Interacts with the SQL repository to manage persistent course data.
    """

    def __init__(
        self,
        sql_repo: ISQLRepository,
        vector_repo: IVectorRepository,
    ):
        self.sql_repo = sql_repo
        self.vector_repo = vector_repo

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
        year: int,
        rag_strategy: Optional[str] = None,
    ) -> dict:
        """
        1️⃣ Validate that instructor exists.
        2️⃣ Persist new course record in the database.
        3. Create collection for course in vector db
        """
        instructor = self.sql_repo.read_instructor(instructor_id)
        if not instructor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instructor with id={instructor_id} not found."
            )

        course = self.sql_repo.read_course_by_name(name, instructor_id)
        if course:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Course '{name}' already exists for instructor {instructor_id}."
            )

        rag_strategy_id: Optional[int] = None
        if rag_strategy is not None:
            strategy_row = self.sql_repo.read_rag_strategy_by_type(rag_strategy)
            if not strategy_row:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Invalid rag_strategy '{rag_strategy}'.")
            rag_strategy_id = strategy_row["id"]

        course_id = self.sql_repo.create_course(
            instructor_id=instructor_id,
            name=name,
            institution=institution,
            semester_id=semester_id,
            year=year,
            rag_strategy_id=rag_strategy_id
        )

        # Step 3: create Chroma/Vector collection
        try:
            self.vector_repo.create_collection(course_id, embedding_function=None, metric=None)
        except Exception as e:
            self.sql_repo.delete_course(course_id)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to initialize vector collection for course {course_id}: {str(e)}")

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
        instructor_email: Optional[str] = None,
        institution: Optional[str] = None,
        status: Optional[str] = None,
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
            instructor_email=instructor_email,
            institution=institution,
            status=status,
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

        # Delete from vector storage
        self.vector_repo.delete_collection(course_id)

        return {"status": "deleted", "course_id": course_id}
    
    # ------------------------------------------------------
    # Get Course ID by Name
    # ------------------------------------------------------
    @clean_service
    def get_course_id_by_name(self, course_name: str) -> dict:
        """
        Retrieve the unique course_id for a given course name.
        """
        course = self.sql_repo.get_course_by_name(course_name)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with name='{course_name}' not found."
            )

        return {"course_id": course["id"]}

    # ------------------------------------------------------
    # Update Course
    # ------------------------------------------------------
    @clean_service
    def update_course(self, course_id: str, updates: dict) -> dict:
        """
        Update course details such as name, institution, semester_id, or year.
        Returns the updated course record.
        """
        existing_course = self.sql_repo.read_course(course_id)
        if not existing_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with id={course_id} not found."
            )

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update."
            )

        updated_course = self.sql_repo.update_course(course_id, updates)
        return updated_course
    
    # ------------------------------------------------------
    # Get Course Count
    # ------------------------------------------------------
    @clean_service
    def count_courses(self) -> int:
        return self.sql_repo.count_courses()

    @clean_service
    def count_courses_grouped_by_instructor(self) -> dict:
        return self.sql_repo.count_courses_grouped_by_instructor()

    # ------------------------------------------------------
    # Canvas integration helpers
    # ------------------------------------------------------
    @clean_service
    def get_course_by_canvas_id(self, canvas_course_id: str) -> dict:
        """Lookup internal course using a Canvas course identifier."""
        course = self.sql_repo.read_course_by_canvas_id(canvas_course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No course linked to Canvas course id={canvas_course_id}."
            )
        return course

    @clean_service
    def link_canvas_course(self, course_id: str, canvas_context_id: str, canvas_course_id: str) -> dict:
        """Associate an existing course (by ID) with a Canvas context and course id."""
        course = self.sql_repo.read_course(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with id={course_id} not found."
            )
        # update record
        updated = self.sql_repo.update_course(course["id"], {"canvas_course_id": canvas_course_id, "canvas_context_id": canvas_context_id})
        return {"course_id": course["id"]}