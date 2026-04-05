from fastapi import HTTPException, status
from typing import Optional
from API.Repository.i_sql_repository import ISQLRepository
from API.Service.gmail_service import GmailService
from API.Util.decorators import clean_service
from API.Util.auth import generate_password_reset_code, verify_password, encrypt_password, encrypt_access_token


class AuthService:
    """Handles instructor authentication and account management."""

    def __init__(self, sql_repo: ISQLRepository, gmail_service: GmailService):
        self.sql_repo = sql_repo
        self.gmail_service = gmail_service

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
    
    @clean_service
    def request_password_reset(self, instructor_email: str) -> dict:
        """Generate and email a 6-digit password reset code."""
        instructor = self.sql_repo.read_instructor_by_email(instructor_email)
        if not instructor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor email not found")

        reset_code = generate_password_reset_code()

        self.sql_repo.create_password_reset_code(instructor_id=instructor["id"], code=reset_code)
        self.gmail_service.send_password_reset_email(to_email=instructor_email, reset_code=reset_code)

        return {"message": "Password reset code sent successfully"}
    

    @clean_service
    def confirm_password_reset(self, instructor_email: str, code: str, new_password: str) -> dict:
        """Verify reset code and update the instructor password."""
        instructor = self.sql_repo.read_instructor_by_email(instructor_email)
        if not instructor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor email not found")

        reset_record = self.sql_repo.read_password_reset_code(instructor["id"])
        if not reset_record or reset_record["code"] != code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset code.")

        self.sql_repo.update_instructor_password(instructor_id=instructor["id"], encrypted_password=encrypt_password(new_password))

        return {"message": "Password reset successful"}