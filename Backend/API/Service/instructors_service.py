from fastapi import HTTPException, status
from typing import List, Optional

from API.Repository.i_sql_repository import ISQLRepository
from API.Util.decorators import clean_service
from API.Util.auth import encrypt_password


class InstructorService:
    """
    Handles creation, retrieval, listing, and deletion of instructors.
    Interacts with the SQL repository to manage persistent instructor data.
    """

    def __init__(self, sql_repo: ISQLRepository):
        self.sql_repo = sql_repo

    # ------------------------------------------------------
    # Create Instructor
    # ------------------------------------------------------
    @clean_service
    def create_instructor(self, name: str, title: str, university: str, email: str, password: str) -> dict:
        """Create a new instructor record in the database."""
        existing = self.sql_repo.read_instructor_by_email(email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Instructor with email={email} already exists.")

        instructor_id = self.sql_repo.create_instructor(name, title, university, email, encrypt_password(password))
        return {"instructor_id": instructor_id}

    # ------------------------------------------------------
    # Read Single Instructor
    # ------------------------------------------------------
    @clean_service
    def read_instructor(self, instructor_id: str) -> dict:
        """Fetch one instructor by its unique ID."""
        instructor = self.sql_repo.read_instructor(instructor_id)
        if not instructor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Instructor with id={instructor_id} not found.")
        return instructor

    # ------------------------------------------------------
    # Read All Instructors
    # ------------------------------------------------------
    @clean_service
    def read_all_instructors(
        self,
        name: Optional[str] = None,
        title: Optional[str] = None,
        university: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "created_at",
        order_dir: str = "desc",
    ) -> List[dict]:
        """Fetch all instructors with optional filters and pagination."""
        return self.sql_repo.read_all_instructors(
            name=name,
            title=title,
            university=university,
            email=email,
            role=role,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_dir=order_dir,
        )

    # ------------------------------------------------------
    # Delete Instructor
    # ------------------------------------------------------
    @clean_service
    def delete_instructor(self, instructor_id: str) -> dict:
        """Remove an instructor record permanently from the database."""
        instructor = self.sql_repo.read_instructor(instructor_id)
        if not instructor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Instructor with id={instructor_id} not found.")

        self.sql_repo.delete_instructor(instructor_id)
        return {"status": "deleted", "instructor_id": instructor_id}
    
    # ------------------------------------------------------
    # Update Instructor
    # ------------------------------------------------------
    @clean_service
    def update_instructor(
        self,
        instructor_id: str,
        name: Optional[str] = None,
        title: Optional[str] = None,
        university: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> dict:
        """Update an existing instructor's information."""

        instructor = self.sql_repo.read_instructor(instructor_id)
        if not instructor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instructor with id={instructor_id} not found."
            )

        # Prepare updates
        updates = {}
        if name:
            updates["name"] = name
        if title:
            updates["title"] = title
        if university:
            updates["university"] = university
        if email:
            # Make sure email is unique
            existing = self.sql_repo.read_instructor_by_email(email)
            if existing and existing["id"] != instructor_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Instructor with email={email} already exists."
                )
            updates["email"] = email
        if password:
            updates["password"] = encrypt_password(password)

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update."
            )

        updated_instructor = self.sql_repo.update_instructor(instructor_id, updates)
        return updated_instructor
