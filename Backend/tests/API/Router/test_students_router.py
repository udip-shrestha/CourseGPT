import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from uuid import uuid4
from API.Routers.students_router import router as student_router
from API.Service.students_service import StudentService
from API.Repository.i_sql_repository import ISQLRepository


@pytest.fixture
def mock_sql_repo() -> ISQLRepository:
    """Mocked SQL repository (contains all methods used by StudentService)."""
    return MagicMock(spec=ISQLRepository)


@pytest.fixture
def student_service(mock_sql_repo: ISQLRepository) -> StudentService:
    """StudentService wired to the mock SQL repo (no vector repo needed)."""
    return StudentService(sql_repo=mock_sql_repo)


@pytest.fixture
def client(student_service: StudentService) -> TestClient:
    """FastAPI test client with the student router and dependency override."""
    from API.dependencies import get_student_service

    app = FastAPI()
    app.include_router(student_router)
    app.dependency_overrides[get_student_service] = lambda: student_service
    return TestClient(app)

def test_is_registered_discord_true(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    """Student is enrolled → registered=True."""
    student_uuid = str(uuid4())
    mock_sql_repo.read_all_students.return_value = [
        {"id": student_uuid, "discord_id": "discord_123", "name": "Alice"}
    ]

    response = client.get(
        "/students/is_registered_discord",
        params={"discord_id": "discord_123", "course_id": "course-1"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"registered": True, "student_id": student_uuid}
    mock_sql_repo.read_all_students.assert_called_once_with(course_id="course-1")


def test_is_registered_discord_false(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    """Student not enrolled → registered=False."""
    mock_sql_repo.read_all_students.return_value = [
        {"id": str(uuid4()), "discord_id": "discord_999", "name": "Bob"}
    ]

    response = client.get(
        "/students/is_registered_discord",
        params={"discord_id": "discord_123", "course_id": "course-1"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"registered": False, "student_id": None}
    mock_sql_repo.read_all_students.assert_called_once_with(course_id="course-1")


def test_is_registered_canvas_true(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    student_uuid = str(uuid4())
    mock_sql_repo.read_student_by_canvas = MagicMock(return_value={"id": student_uuid})
    mock_sql_repo.read_all_students = MagicMock(return_value=[{"id": student_uuid}])

    response = client.get(
        "/students/is_registered_canvas",
        params={"canvas_user_id": "can123", "course_id": "course-1"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"registered": True, "student_id": student_uuid}


def test_is_registered_canvas_false(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    mock_sql_repo.read_student_by_canvas = MagicMock(return_value=None)

    response = client.get(
        "/students/is_registered_canvas",
        params={"canvas_user_id": "can123", "course_id": "course-1"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"registered": False, "student_id": None}

def test_get_registered_courses_success(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    """Return all courses linked to a Discord ID."""
    mock_courses = [
        {
            "course_id": str(uuid4()),
            "course_name": "CS101",
            "institution": "Iowa State",
            "year": "2025",
            "student_id": str(uuid4()),
            "student_name": "Alice",
            "discord_id": "discord_123",
        }
    ]
    mock_sql_repo.read_courses_by_discord.return_value = mock_courses

    response = client.get("/students/discord_123/courses")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"courses": mock_courses}
    mock_sql_repo.read_courses_by_discord.assert_called_once_with("discord_123")

def test_register_student_with_canvas_id(client: TestClient, mock_sql_repo: ISQLRepository):
    mock_sql_repo.create_student.return_value = "s3"
    response = client.post(
        "/students/register",
        params={
            "name": "Eve",
            "course_id": "c1",
            "canvas_user_id": "can-5",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    mock_sql_repo.create_student.assert_called_once_with(
        name="Eve",
        discord_id=None,
        course_id="c1",
        canvas_user_id="can-5",
    )

def test_get_registered_courses_not_found(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    """No courses → empty list."""
    mock_sql_repo.read_courses_by_discord.return_value = []

    response = client.get("/students/discord_999/courses")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"courses": []}
    mock_sql_repo.read_courses_by_discord.assert_called_once_with("discord_999")

def test_unregister_student_success(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    student_uuid = str(uuid4())
    mock_sql_repo.read_student_by_discord.return_value = {"id": student_uuid}
    mock_sql_repo.remove_student_from_course.return_value = True   # <-- positional call

    response = client.delete(
        "/students/unregister",
        params={"discord_id": "d123", "course_id": "c1"},
    )

    assert response.status_code == status.HTTP_200_OK
    mock_sql_repo.read_student_by_discord.assert_called_once_with("d123")
    mock_sql_repo.remove_student_from_course.assert_called_once_with(
        student_uuid, "c1"          # exact positional args used by the service
    )

def test_unregister_student_exception(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    """Unexpected DB error → 500."""
    student_uuid = str(uuid4())
    mock_sql_repo.read_student_by_discord.return_value = {"id": student_uuid}
    mock_sql_repo.remove_student_from_course.side_effect = Exception("DB error")

    response = client.delete(
        "/students/unregister",
        params={"discord_id": "discord_123", "course_id": "course-1"},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to unregister student" in response.json()["detail"]

    mock_sql_repo.read_student_by_discord.assert_called_once_with("discord_123")