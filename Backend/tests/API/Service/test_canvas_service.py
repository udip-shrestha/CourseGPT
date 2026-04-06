import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException, status
from API.Service.courses_service import CourseService
from API.Service.students_service import StudentService
from API.Repository.i_sql_repository import ISQLRepository


def test_get_course_by_canvas_id_success(course_service: CourseService, mock_sql_repo: ISQLRepository):
    # add Canvas methods to mock (they may not be in ISQLRepository spec)
    mock_sql_repo.read_course_by_canvas_id = MagicMock(return_value={"id": "c1"})
    result = course_service.get_course_by_canvas_id("canvas-xyz")
    mock_sql_repo.read_course_by_canvas_id.assert_called_once_with("canvas-xyz")
    assert result["id"] == "c1"


def test_get_course_by_canvas_id_not_found(course_service: CourseService, mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_course_by_canvas_id = MagicMock(return_value=None)
    with pytest.raises(HTTPException) as exc_info:
        course_service.get_course_by_canvas_id("canvas-missing")
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_link_canvas_course_success(course_service: CourseService, mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_course.return_value = {"id": "c2"}
    mock_sql_repo.update_course.return_value = {"id": "c2"}
    result = course_service.link_canvas_course("c2", "canvas-ctx-456", "canvas-123")
    mock_sql_repo.read_course.assert_called_once_with("c2")
    mock_sql_repo.update_course.assert_called_once_with("c2", {"canvas_course_id": "canvas-123", "canvas_context_id": "canvas-ctx-456"})
    assert result == {"course_id": "c2"}


def test_link_canvas_course_not_found(course_service: CourseService, mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_course.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        course_service.link_canvas_course("Unknown", "canvas-abc", "canvas-ctx-789")
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


# student service canvas helpers

def test_find_student_canvas_not_registered(student_service: StudentService, mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_student_by_canvas = MagicMock(return_value=None)
    result = student_service.find_student_in_course_by_canvas("canvas-1", "course-1")
    assert result is None


def test_find_student_canvas_registered(student_service: StudentService, mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_student_by_canvas = MagicMock(return_value={"id": "s1", "name": "Bob"})
    mock_sql_repo.read_all_students = MagicMock(return_value=[{"id": "s1"}])
    result = student_service.find_student_in_course_by_canvas("canvas-1", "course-1")
    assert result and result.get("id") == "s1"


def test_register_canvas_student(student_service: StudentService, mock_sql_repo: ISQLRepository):
    mock_sql_repo.create_student.return_value = "s2"
    result = student_service.register_canvas_student("Carol", "canvas-2", "course-1")
    mock_sql_repo.create_student.assert_called_once_with(
        name="Carol",
        discord_id=None,
        course_id="course-1",
        canvas_user_id="canvas-2",
    )
    assert result == {"student_id": "s2"}
