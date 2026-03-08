import os
import json
import base64
import pytest
from fastapi import FastAPI, status, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from API.Routers import canvas_router
from API.Service.canvas_service import CanvasService
from API.Service.courses_service import CourseService
from API.Service.students_service import StudentService


@pytest.fixture
def mock_canvas_service() -> CanvasService:
    service = MagicMock(spec=CanvasService)
    # Add redirect_to method to mock
    from fastapi.responses import RedirectResponse
    service.redirect_to = MagicMock(side_effect=lambda base_url, path: RedirectResponse(url=f"{base_url}{path}", status_code=302))
    return service


@pytest.fixture
def mock_course_service() -> CourseService:
    return MagicMock(spec=CourseService)


@pytest.fixture
def mock_student_service() -> StudentService:
    return MagicMock(spec=StudentService)


@pytest.fixture

def client(
    mock_canvas_service: CanvasService,
    mock_course_service: CourseService,
    mock_student_service: StudentService,
) -> TestClient:
    from API.dependencies import (
        get_canvas_service,
        get_course_service,
        get_student_service,
    )

    app = FastAPI()
    app.include_router(canvas_router.router)
    app.dependency_overrides[get_canvas_service] = lambda: mock_canvas_service
    app.dependency_overrides[get_course_service] = lambda: mock_course_service
    app.dependency_overrides[get_student_service] = lambda: mock_student_service
    return TestClient(app, follow_redirects=False)


# helper to craft a token without signature verification

def make_id_token(payload: dict) -> str:
    hdr = base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode()).rstrip(b"=").decode()
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    return f"{hdr}.{body}."


# --------------------------------------------------
# LTI login
# --------------------------------------------------

def test_lti_login_redirect():
    """Should redirect to Canvas OIDC endpoint with proper params."""
    app = FastAPI()
    app.include_router(canvas_router.router)
    client = TestClient(app, follow_redirects=False)

    form = {
        "iss": "https://canvas.example.com",
        "login_hint": "hint123",
        "target_link_uri": "https://frontend.example.com/lti/launch",
        "client_id": "cid",
        "lti_deployment_id": "deploy123",
    }
    response = client.post("/lti/login", data=form)
    assert response.status_code == status.HTTP_302_FOUND
    # verify redirect url contains expected query string
    location = response.headers["location"]
    assert location.startswith("https://canvas.example.com/api/lti/authorize_redirect?")
    assert "prompt=none" in location
    assert "client_id=cid" in location
    assert "login_hint=hint123" in location


# --------------------------------------------------
# LTI launch logic
# --------------------------------------------------

def test_lti_launch_instructor_course_linked(
    client: TestClient,
    mock_course_service: CourseService,
):
    os.environ["API_BASE_URL"] = "http://frontend.test"
    payload = {
        "sub": "user1",
        "https://purl.imsglobal.org/spec/lti/claim/context": {"id": "canvas-course"},
        "https://purl.imsglobal.org/spec/lti/claim/roles": ["Instructor"],
    }
    token = make_id_token(payload)
    mock_course_service.get_course_by_canvas_id.return_value = {"id": "internal-42"}

    response = client.post("/lti/launch", data={"id_token": token})
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == "http://frontend.test/courses/internal-42"
    mock_course_service.get_course_by_canvas_id.assert_called_once_with("canvas-course")


def test_lti_launch_instructor_course_not_linked(
    client: TestClient,
    mock_course_service: CourseService,
):
    os.environ["API_BASE_URL"] = "http://frontend.test"
    payload = {
        "sub": "user2",
        "https://purl.imsglobal.org/spec/lti/claim/context": {"id": "uncourse"},
        "https://purl.imsglobal.org/spec/lti/claim/roles": ["Instructor"],
    }
    token = make_id_token(payload)
    # simulate not found by raising HTTPException
    mock_course_service.get_course_by_canvas_id.side_effect = HTTPException(
        status_code=404, detail="Course not linked"
    )

    response = client.post("/lti/launch", data={"id_token": token})
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == "http://frontend.test/register-course?canvas_course_id=uncourse"


def test_lti_launch_student_not_linked_course(
    client: TestClient,
    mock_course_service: CourseService,
):
    os.environ["API_BASE_URL"] = "http://frontend.test"
    payload = {
        "sub": "student1",
        "https://purl.imsglobal.org/spec/lti/claim/context": {"id": "unknown-course"},
        "https://purl.imsglobal.org/spec/lti/claim/roles": ["Learner"],
    }
    token = make_id_token(payload)
    # simulate course not found by raising HTTPException
    mock_course_service.get_course_by_canvas_id.side_effect = HTTPException(
        status_code=404, detail="Course not linked"
    )

    response = client.post("/lti/launch", data={"id_token": token})
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == "http://frontend.test/?error=course_not_linked"


def test_lti_launch_student_requires_registration(
    client: TestClient,
    mock_course_service: CourseService,
    mock_student_service: StudentService,
):
    os.environ["API_BASE_URL"] = "http://frontend.test"
    payload = {
        "sub": "stu2",
        "https://purl.imsglobal.org/spec/lti/claim/context": {"id": "c-course"},
        "https://purl.imsglobal.org/spec/lti/claim/roles": ["Learner"],
    }
    token = make_id_token(payload)
    mock_course_service.get_course_by_canvas_id.return_value = {"id": "int-9"}
    mock_student_service.find_student_in_course_by_canvas.return_value = None

    response = client.post("/lti/launch", data={"id_token": token})
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == (
        "http://frontend.test/courses/int-9/chats?role=student&needs_registration=1&"
        "canvas_user_id=stu2"
    )


def test_lti_launch_student_already_registered(
    client: TestClient,
    mock_course_service: CourseService,
    mock_student_service: StudentService,
):
    os.environ["API_BASE_URL"] = "http://frontend.test"
    payload = {
        "sub": "stu3",
        "https://purl.imsglobal.org/spec/lti/claim/context": {"id": "c-course2"},
        "https://purl.imsglobal.org/spec/lti/claim/roles": ["Learner"],
    }
    token = make_id_token(payload)
    mock_course_service.get_course_by_canvas_id.return_value = {"id": "int-10"}
    mock_student_service.find_student_in_course_by_canvas.return_value = {"id": "s123"}

    response = client.post("/lti/launch", data={"id_token": token})
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == "http://frontend.test/courses/int-10/chats?role=student"
