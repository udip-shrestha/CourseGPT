import pytest
from fastapi import HTTPException, status
from API.Service.instructors_service import InstructorService
from API.Repository.i_sql_repository import ISQLRepository


def test_create_instructor_success(mock_sql_repo: ISQLRepository):
    """Should create an instructor when email not used."""
    mock_sql_repo.read_instructor_by_email.return_value = None
    mock_sql_repo.create_instructor.return_value = "inst-123"

    service = InstructorService(mock_sql_repo)
    result = service.create_instructor("John Doe", "Professor", "Iowa State", "john@isu.edu")

    mock_sql_repo.read_instructor_by_email.assert_called_once_with("john@isu.edu")
    mock_sql_repo.create_instructor.assert_called_once()
    assert result == {"instructor_id": "inst-123"}


def test_create_instructor_duplicate_email(mock_sql_repo: ISQLRepository):
    """Should raise 400 if instructor email already exists."""
    mock_sql_repo.read_instructor_by_email.return_value = {"id": "inst-1"}

    service = InstructorService(mock_sql_repo)
    with pytest.raises(HTTPException) as exc_info:
        service.create_instructor("John", "Prof", "ISU", "john@isu.edu")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in exc_info.value.detail


def test_read_instructor_success(mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_instructor.return_value = {"id": "i1", "name": "John"}
    service = InstructorService(mock_sql_repo)

    result = service.read_instructor("i1")

    assert result["name"] == "John"
    mock_sql_repo.read_instructor.assert_called_once_with("i1")


def test_read_instructor_not_found(mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_instructor.return_value = None
    service = InstructorService(mock_sql_repo)

    with pytest.raises(HTTPException) as exc_info:
        service.read_instructor("not-found")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_read_all_instructors(mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_all_instructors.return_value = [{"name": "A"}, {"name": "B"}]
    service = InstructorService(mock_sql_repo)

    results = service.read_all_instructors(limit=5, offset=0)

    assert len(results) == 2
    mock_sql_repo.read_all_instructors.assert_called_once()


def test_delete_instructor_success(mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_instructor.return_value = {"id": "i1"}
    service = InstructorService(mock_sql_repo)

    result = service.delete_instructor("i1")

    mock_sql_repo.delete_instructor.assert_called_once_with("i1")
    assert result == {"status": "deleted", "instructor_id": "i1"}


def test_delete_instructor_not_found(mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_instructor.return_value = None
    service = InstructorService(mock_sql_repo)

    with pytest.raises(HTTPException) as exc_info:
        service.delete_instructor("fake")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
