import pytest
from fastapi import HTTPException, status
from API.Service.instructors_service import InstructorService
from API.Repository.i_sql_repository import ISQLRepository
from unittest.mock import patch


def test_read_instructor_success(instructor_service: InstructorService, mock_sql_repo: ISQLRepository):
    """Should return instructor when found."""
    mock_sql_repo.read_instructor.return_value = {"id": "i1", "name": "John"}

    result = instructor_service.read_instructor("i1")

    assert result["name"] == "John"
    mock_sql_repo.read_instructor.assert_called_once_with("i1")


def test_read_instructor_not_found(instructor_service: InstructorService, mock_sql_repo: ISQLRepository):
    """Should raise 404 when instructor not found."""
    mock_sql_repo.read_instructor.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        instructor_service.read_instructor("not-found")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_read_instructor_not_found(mock_sql_repo: ISQLRepository):
    """Should raise 404 when instructor not found."""
    mock_sql_repo.read_instructor.return_value = None
    service = InstructorService(mock_sql_repo)

    with pytest.raises(HTTPException) as exc_info:
        service.read_instructor("not-found")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_read_all_instructors(instructor_service: InstructorService, mock_sql_repo: ISQLRepository):
    """Should return all instructors and pass filter params correctly."""
    mock_sql_repo.read_all_instructors.return_value = [{"name": "A"}, {"name": "B"}]

    results = instructor_service.read_all_instructors(
        name="John", email="john@isu.edu", limit=5, offset=1, role="INSTRUCTOR"
    )

    mock_sql_repo.read_all_instructors.assert_called_once_with(
        name="John",
        title=None,
        university=None,
        email="john@isu.edu",
        role="INSTRUCTOR",
        limit=5,
        offset=1,
        order_by="created_at",
        order_dir="desc",
    )
    assert len(results) == 2

def test_delete_instructor_success(instructor_service: InstructorService, mock_sql_repo: ISQLRepository):
    """Should delete instructor successfully."""
    mock_sql_repo.read_instructor.return_value = {"id": "i1"}

    result = instructor_service.delete_instructor("i1")

    mock_sql_repo.delete_instructor.assert_called_once_with("i1")
    assert result == {"status": "deleted", "instructor_id": "i1"}


def test_delete_instructor_not_found(instructor_service: InstructorService, mock_sql_repo: ISQLRepository):
    """Should raise 404 if instructor does not exist."""
    mock_sql_repo.read_instructor.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        instructor_service.delete_instructor("fake")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND