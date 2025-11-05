import pytest
from fastapi import HTTPException, status
from API.Service.students_service import StudentService
from API.Repository.i_sql_repository import ISQLRepository
from API.Repository.i_vector_repository import IVectorRepository

# -------------------------------
# Example: create student test
# -------------------------------
def test_create_student_success(student_service: StudentService, mock_sql_repo: ISQLRepository):
    """Should create a student if not exists."""
    # Mock SQL repo to simulate new student creation
    mock_sql_repo.create_student.return_value = "student-1"
    mock_sql_repo.read_student_by_discord.return_value = None

    result = student_service.create_student("Alice", "discord-123", "course-1")

    mock_sql_repo.create_student.assert_called_once_with(
       name="Alice", 
       discord_id="discord-123", 
       course_id="course-1"
    )
    assert result == {"student_id": "student-1"}


def test_create_student_already_registered(student_service: StudentService, mock_sql_repo: ISQLRepository):
    """Should return existing student_id if student already exists and is linked to course.
    The repository handles this internally."""
    mock_sql_repo.create_student.return_value = "student-1"

    result = student_service.create_student("Alice", "discord-123", "course-1")

    mock_sql_repo.create_student.assert_called_once_with(
        name="Alice",
        discord_id="discord-123", 
        course_id="course-1"
    )
    assert result == {"student_id": "student-1"}


def test_read_student_success(student_service: StudentService, mock_sql_repo: ISQLRepository):
    """Should return student info if exists."""
    mock_sql_repo.read_student.return_value = {"id": "student-1", "name": "Alice"}

    result = student_service.read_student("student-1")

    mock_sql_repo.read_student.assert_called_once_with("student-1")
    assert result["name"] == "Alice"


def test_read_student_not_found(student_service: StudentService, mock_sql_repo: ISQLRepository):
    """Should raise 404 if student not found."""
    mock_sql_repo.read_student.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        student_service.read_student("fake-id")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_delete_student_success(student_service: StudentService, mock_sql_repo: ISQLRepository):
    """Should delete student if exists."""
    mock_sql_repo.read_student.return_value = {"id": "student-1"}

    result = student_service.delete_student("student-1")

    mock_sql_repo.delete_student.assert_called_once_with("student-1")
    assert result == {"status": "deleted", "student_id": "student-1"}


def test_delete_student_not_found(student_service: StudentService, mock_sql_repo: ISQLRepository):
    """Should raise 404 if student does not exist."""
    mock_sql_repo.read_student.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        student_service.delete_student("fake-id")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
