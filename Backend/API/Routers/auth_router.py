from fastapi import APIRouter, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from API.Service.auth_service import AuthService
from API.dependencies import get_auth_service

router = APIRouter(tags=["Auth"])


@router.post(
    "/auth/login",
    status_code=status.HTTP_200_OK,
    summary="Authenticate instructor and issue access token",
    description=(
        "**Action:** Authenticates instructor credentials using OAuth2 Password Grant. "
        "Validates the provided email and password, and returns a signed JWT access token.\n\n"
        "**Form Fields:**\n"
        "- `username`: Instructor's email address\n"
        "- `password`: Instructor's password\n\n"
        "**Returns:** JSON containing `access_token` and `token_type`."
    ),
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    """OAuth2-compliant login endpoint for instructors."""
    return service.login(
        instructor_email=form_data.username,
        instructor_password=form_data.password
    )

@router.post(
    "/auth/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new instructor and return JWT access token",
    description=(
        "Registers a new instructor using form fields and returns a signed JWT token. "
        "No admin privileges required."
    ),
)
def register(
    name: str = Form("Dr. Jane Doe", description="Full name of the instructor"),
    title: str = Form("Assistant Professor of Computer Science", description="Instructor's title"),
    university: str = Form("Iowa State University", description="Instructor's university"),
    email: str = Form("jane.doe@iastate.edu", description="Instructor's email address"),
    password: str = Form("mysecurepassword", description="Instructor's password"),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Public registration endpoint that returns access token."""
    return auth_service.register(name=name, title=title, university=university, email=email, password=password)