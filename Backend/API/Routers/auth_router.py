from fastapi import APIRouter, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from Metrics.metrics import MetricsRoute
from API.Service.auth_service import AuthService
from API.dependencies import get_auth_service

router = APIRouter(tags=["Auth"], route_class=MetricsRoute)


# ---------------------------------------------------------------------
# Login (OAuth2 Password Grant)
# ---------------------------------------------------------------------
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
    service: AuthService = Depends(get_auth_service),
):
    """OAuth2-compliant login endpoint for instructors."""
    return service.login(
        instructor_email=form_data.username,
        instructor_password=form_data.password,
    )


# ---------------------------------------------------------------------
# Register Instructor
# ---------------------------------------------------------------------
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
    name: str = Form(
        ...,
        examples=["Dr. Jane Doe"],
        description="Full name of the instructor",
    ),
    title: str = Form(
        ...,
        examples=["Assistant Professor of Computer Science"],
        description="Instructor's title",
    ),
    university: str = Form(
        ...,
        examples=["Iowa State University"],
        description="Instructor's university",
    ),
    email: str = Form(
        ...,
        examples=["jane.doe@iastate.edu"],
        description="Instructor's email address",
    ),
    password: str = Form(
        ...,
        examples=["mysecurepassword"],
        description="Instructor's password",
    ),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Public registration endpoint that returns access token."""
    return auth_service.register(name=name, title=title, university=university, email=email, password=password)


# ---------------------------------------------------------------------
# Request Password Reset Code
# ---------------------------------------------------------------------
@router.post(
    "/auth/request-password-reset",
    status_code=status.HTTP_200_OK,
    summary="Send a password reset code to instructor email",
    description=(
        "Generates a 6-digit password reset code for the instructor account "
        "associated with the provided email and sends it by email."
    ),
)
def request_password_reset(
    email: str = Form(
        ...,
        examples=["jane.doe@iastate.edu"],
        description="Instructor's email address",
    ),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Request a password reset code."""
    return auth_service.request_password_reset(instructor_email=email)


# ---------------------------------------------------------------------
# Confirm Password Reset
# ---------------------------------------------------------------------
@router.post(
    "/auth/confirm-password-reset",
    status_code=status.HTTP_200_OK,
    summary="Verify password reset code and set a new password",
    description=(
        "Verifies the 6-digit password reset code sent to the instructor's email "
        "and updates the instructor password."
    ),
)
def confirm_password_reset(
    email: str = Form(
        ...,
        examples=["jane.doe@iastate.edu"],
        description="Instructor's email address",
    ),
    code: str = Form(
        ...,
        examples=["123456"],
        description="6-digit password reset code",
    ),
    new_password: str = Form(
        ...,
        examples=["mynewsecurepassword"],
        description="New password for the instructor account",
    ),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Confirm password reset using the emailed code."""
    return auth_service.confirm_password_reset(
        instructor_email=email,
        code=code,
        new_password=new_password,
    )

