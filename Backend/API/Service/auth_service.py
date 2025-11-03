from fastapi import HTTPException, status
from typing import Optional
from API.Repository.i_sql_repository import ISQLRepository
from API.Util.decorators import clean_service
from API.Util.auth import verify_password, encrypt_password, encrypt_access_token


class AuthService:
    """Handles instructor authentication and account management."""

    def __init__(self, sql_repo: ISQLRepository):
        self.sql_repo = sql_repo

    @clean_service
    def login(self, instructor_email: str, instructor_password: str) -> dict:
        """Authenticate instructor credentials and return a JWT token."""
        instructor = self.sql_repo.read_instructor_by_email(instructor_email)
        if not instructor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor email not found")

        if not verify_password(instructor["password"], instructor_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

        instructor_id = instructor["id"]
        access_token = encrypt_access_token({"id": instructor_id})
        return {"access_token": access_token, "token_type": "bearer", "instructor_id": instructor_id}

    @clean_service
    def register(self, name: str, title: str, university: str, email: str, password: str) -> dict:
        """Register a new instructor and return a JWT token."""
        existing = self.sql_repo.read_instructor_by_email(email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        instructor_id = self.sql_repo.create_instructor(name=name, title=title, university=university, email=email, encrypted_password=encrypt_password(password))

        access_token = encrypt_access_token({"id": instructor_id})
        return {"access_token": access_token, "token_type": "bearer", "instructor_id": instructor_id}