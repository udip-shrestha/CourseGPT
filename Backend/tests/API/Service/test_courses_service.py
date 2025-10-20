import pytest
from fastapi import HTTPException, status
from API.Service.courses_service import CourseService
from API.Repository.i_sql_repository import ISQLRepository


def test_create_course_success(mock_sql_repo: ISQLRepository):
    """Should create a course if instructor exists."""
    mock_sql_repo.read_instructor.return_value = {"id": "inst-1"}
    mock_sql_repo.create_course.return_value = "course-1"

    service = CourseService(mock_sql_repo)
    result = service.create_course("inst-1", "CS101", "Iowa State", 1, 2025)

    mock_sql_repo.create_course.assert_called_once()
    assert result == {"course_id": "course-1"}


def test_create_course_instructor_not_found(mock_sql_repo: ISQLRepository):
    """Should raise 404 if instructor does not exist."""
    mock_sql_repo.read_instructor.return_value = None
    service = CourseService(mock_sql_repo)

    with pytest.raises(HTTPException) as exc_info:
        service.create_course("fake-inst", "CS101", "ISU", 1, 2025)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail.lower()


def test_read_course_success(mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_course.return_value = {"id": "c1", "name": "CS101"}
    service = CourseService(mock_sql_repo)

    result = service.read_course("c1")

    assert result["name"] == "CS101"
    mock_sql_repo.read_course.assert_called_once_with("c1")


def test_read_course_not_found(mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_course.return_value = None
    service = CourseService(mock_sql_repo)

    with pytest.raises(HTTPException) as exc_info:
        service.read_course("fake")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_read_all_courses(mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_all_courses.return_value = [{"name": "CS101"}, {"name": "CS102"}]
    service = CourseService(mock_sql_repo)

    result = service.read_all_courses(institution="Iowa")

    assert len(result) == 2
    mock_sql_repo.read_all_courses.assert_called_once()


def test_delete_course_success(mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_course.return_value = {"id": "c1"}
    service = CourseService(mock_sql_repo)

    result = service.delete_course("c1")

    mock_sql_repo.delete_course.assert_called_once_with("c1")
    assert result == {"status": "deleted", "course_id": "c1"}


def test_delete_course_not_found(mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_course.return_value = None
    service = CourseService(mock_sql_repo)

    with pytest.raises(HTTPException) as exc_info:
        service.delete_course("fake")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
