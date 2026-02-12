import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from API.Routers.courses_router import router as courses_router
from API.Service.courses_service import CourseService
from API.Repository.i_sql_repository import ISQLRepository
from API.Repository.i_vector_repository import IVectorRepository


@pytest.fixture
def mock_sql_repo() -> ISQLRepository:
    """Provides a mocked SQL repository instance."""
    return MagicMock(spec=ISQLRepository)


@pytest.fixture
def mock_vector_repo() -> IVectorRepository:
    """Provides a mocked vector repository instance."""
    return MagicMock(spec=IVectorRepository)


@pytest.fixture
def course_service(mock_sql_repo: ISQLRepository, mock_vector_repo: IVectorRepository) -> CourseService:
    """Provides a CourseService instance with mock repositories."""
    return CourseService(sql_repo=mock_sql_repo, vector_repo=mock_vector_repo)


@pytest.fixture
def client(course_service: CourseService) -> TestClient:
    """Create a test client with dependency overrides."""
    from API.dependencies import get_course_service
    
    app = FastAPI()
    app.include_router(courses_router)
    # Override the dependency function, not the class
    app.dependency_overrides[get_course_service] = lambda: course_service
    return TestClient(app)


def test_add_course_success(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
    mock_vector_repo: IVectorRepository
):
    """Should create a course if instructor exists."""
    # Configure mock returns
    mock_sql_repo.read_instructor.return_value = {"id": "inst-1"}
    mock_sql_repo.read_course_by_name.return_value = None  # REQUIRED
    mock_sql_repo.create_course.return_value = "course-1"
    mock_vector_repo.create_collection.return_value = None

    # Make request
    response = client.post(
        "/instructors/inst-1/courses",
        params={
            "name": "CS101",
            "institution": "Iowa State",
            "semester_id": 1,
            "year": 2025
        }
    )

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"course_id": "course-1"}
    mock_sql_repo.read_instructor.assert_called_once_with("inst-1")
    mock_sql_repo.create_course.assert_called_once()
    mock_vector_repo.create_collection.assert_called_once()


def test_add_course_instructor_not_found(
    client: TestClient,
    mock_sql_repo: ISQLRepository
):
    """Should raise 404 if instructor does not exist."""
    # Configure mock to return None (instructor not found)
    mock_sql_repo.read_instructor.return_value = None

    # Make request
    response = client.post(
        "/instructors/invalid-id/courses",
        params={
            "name": "CS101",
            "institution": "Iowa State",
            "semester_id": 1,
            "year": 2025
        }
    )

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_sql_repo.read_instructor.assert_called_once_with("invalid-id")


def test_get_all_courses(
    client: TestClient,
    mock_sql_repo: ISQLRepository
):
    """Should retrieve all courses for an instructor."""
    # Configure mock returns
    mock_courses = [
        {
            "id": "course-1",
            "name": "CS101",
            "institution": "Iowa State",
            "semester_id": 1,
            "year": 2025
        },
        {
            "id": "course-2",
            "name": "CS201",
            "institution": "Iowa State",
            "semester_id": 1,
            "year": 2025
        }
    ]
    mock_sql_repo.read_all_courses.return_value = mock_courses

    # Make request
    response = client.get("/instructors/inst-1/courses")

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    mock_sql_repo.read_all_courses.assert_called_once()


def test_get_course_by_id_success(
    client: TestClient,
    mock_sql_repo: ISQLRepository
):
    """Should retrieve a course by its ID."""
    # Configure mock returns
    mock_course = {
        "id": "course-1",
        "name": "CS101",
        "institution": "Iowa State",
        "semester_id": 1,
        "year": 2025
    }
    mock_sql_repo.read_course.return_value = mock_course

    # Make request
    response = client.get("/courses/course-1")

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == "course-1"
    mock_sql_repo.read_course.assert_called_once_with("course-1")


def test_get_course_by_id_not_found(
    client: TestClient,
    mock_sql_repo: ISQLRepository
):
    """Should raise 404 if course does not exist."""
    # Configure mock to return None
    mock_sql_repo.read_course.return_value = None

    # Make request
    response = client.get("/courses/invalid-id")

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_sql_repo.read_course.assert_called_once_with("invalid-id")


def test_delete_course_success(
    client: TestClient,
    mock_sql_repo: ISQLRepository,
    mock_vector_repo: IVectorRepository
):
    """Should delete a course and its vector collection."""
    # Configure mock returns
    mock_sql_repo.delete_course.return_value = None
    mock_vector_repo.delete_collection.return_value = None

    # Make request
    response = client.delete("/courses/course-1")

    # Assertions
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_sql_repo.delete_course.assert_called_once_with("course-1")
    mock_vector_repo.delete_collection.assert_called_once_with("course-1")


def test_get_course_id_by_name_success(
    client: TestClient,
    course_service: CourseService,
    mock_sql_repo: ISQLRepository
):
    """Should retrieve course ID by course name."""
    # Configure mock returns - ensure the method exists on the mock
    mock_sql_repo.get_course_by_name.return_value = {"id": "course-1"}

    # Make request
    response = client.get("/courses", params={"course_name": "CS101"})

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"course_id": "course-1"}
    mock_sql_repo.get_course_by_name.assert_called_once_with("CS101")


def test_get_course_id_by_name_not_found(
    client: TestClient,
    course_service: CourseService,
    mock_sql_repo: ISQLRepository
):
    """Should raise 404 if course name does not exist."""
    # Configure mock to return None
    mock_sql_repo.get_course_by_name.return_value = None

    # Make request
    response = client.get("/courses", params={"course_name": "NonExistent"})

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_sql_repo.get_course_by_name.assert_called_once_with("NonExistent")