import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from uuid import uuid4
from API.Routers.instructors_router import router as instructor_router
from API.Service.instructors_service import InstructorService
from API.Repository.i_sql_repository import ISQLRepository
from unittest.mock import patch

@pytest.fixture
def mock_sql_repo() -> ISQLRepository:
    """Provides a mocked SQL repository instance."""
    return MagicMock(spec=ISQLRepository)


@pytest.fixture
def instructor_service(mock_sql_repo: ISQLRepository) -> InstructorService:
    """Provides an InstructorService instance with a mock SQL repository."""
    return InstructorService(sql_repo=mock_sql_repo)


@pytest.fixture
def client(instructor_service: InstructorService) -> TestClient:
    """Create a test client with dependency overrides."""
    from API.dependencies import get_instructor_service

    app = FastAPI()
    app.include_router(instructor_router)
    app.dependency_overrides[get_instructor_service] = lambda: instructor_service
    return TestClient(app)
        
def test_add_instructor_duplicate_email(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    """Should return 400 if email already exists."""
    mock_sql_repo.read_instructor_by_email.return_value = {"id": str(uuid4())}

    response = client.post(
        "/instructors",
        params={
            "name": "Dr. John Doe",
            "title": "Professor",
            "university": "Tech University",
            "email": "john@tech.edu",
            "password": "pass123"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]
    mock_sql_repo.read_instructor_by_email.assert_called_once_with("john@tech.edu")
    mock_sql_repo.create_instructor.assert_not_called()


def test_get_instructor_by_id_success(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    """Should retrieve an instructor by ID."""
    instructor_id = str(uuid4())
    mock_sql_repo.read_instructor.return_value = {
        "id": instructor_id,
        "name": "Dr. Sarah Johnson",
        "title": "Associate Professor",
        "university": "Tech University",
        "email": "sarah@tech.edu",
        "role": "INSTRUCTOR"
    }

    response = client.get(f"/instructors/{instructor_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == instructor_id
    mock_sql_repo.read_instructor.assert_called_once_with(instructor_id)


def test_get_instructor_by_id_not_found(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    """Should return 404 if instructor not found."""
    mock_sql_repo.read_instructor.return_value = None

    response = client.get("/instructors/invalid-uuid")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_sql_repo.read_instructor.assert_called_once_with("invalid-uuid")


def test_get_all_instructors_no_filter(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    """Should return paginated list of all instructors."""
    mock_result = {
        "total": 2,
        "instructors": [
            {"id": str(uuid4()), "name": "Dr. A", "university": "Tech U"},
            {"id": str(uuid4()), "name": "Dr. B", "university": "State U"}
        ]
    }
    mock_sql_repo.read_all_instructors.return_value = mock_result

    response = client.get("/instructors")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 2
    assert len(response.json()["instructors"]) == 2
    mock_sql_repo.read_all_instructors.assert_called_once_with(
        name=None, title=None, university=None, email=None, role=None,
        limit=10, offset=0, order_by="created_at", order_dir="desc"
    )


def test_get_all_instructors_with_university_filter(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    """Should filter instructors by university."""
    mock_result = {
        "total": 1,
        "instructors": [{"id": str(uuid4()), "name": "Dr. Sarah", "university": "Tech University"}]
    }
    mock_sql_repo.read_all_instructors.return_value = mock_result

    response = client.get("/instructors", params={"university": "Tech"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 1
    mock_sql_repo.read_all_instructors.assert_called_once_with(
        name=None, title=None, university="Tech", email=None, role=None,
        limit=10, offset=0, order_by="created_at", order_dir="desc"
    )


def test_delete_instructor_success(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
):
    """Should delete an instructor and return 204."""
    instructor_id = str(uuid4())
    mock_sql_repo.delete_instructor.return_value = None

    response = client.delete(f"/instructors/{instructor_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
    mock_sql_repo.delete_instructor.assert_called_once_with(instructor_id)
