import pytest
from fastapi import HTTPException, status
from API.Service.courses_service import CourseService
from API.Repository.i_sql_repository import ISQLRepository
from API.Repository.i_vector_repository import IVectorRepository


def test_create_course_success(course_service: CourseService, mock_sql_repo: ISQLRepository, mock_vector_repo: IVectorRepository):
    """Should create a course if instructor exists."""
    mock_sql_repo.read_instructor.return_value = {"id": "inst-1"}
    mock_sql_repo.read_course_by_name.return_value = None
    mock_sql_repo.create_course.return_value = "course-1"

    result = course_service.create_course("inst-1", "CS101", "Iowa State", 1, 2025)

    mock_sql_repo.create_course.assert_called_once()
    mock_vector_repo.create_collection.assert_called_once_with("course-1", embedding_function=None, metric=None)
    assert result == {"course_id": "course-1"}


def test_create_course_instructor_not_found(course_service: CourseService, mock_sql_repo: ISQLRepository, mock_vector_repo: IVectorRepository):
    """Should raise 404 if instructor does not exist."""
    mock_sql_repo.read_instructor.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        course_service.create_course("fake-inst", "CS101", "ISU", 1, 2025)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail.lower()
    mock_vector_repo.create_collection.assert_not_called()


def test_create_course_vector_failure_rolls_back(course_service: CourseService, mock_sql_repo: ISQLRepository, mock_vector_repo: IVectorRepository):
    """Should roll back SQL course if vector collection creation fails."""
    mock_sql_repo.read_instructor.return_value = {"id": "inst-1"}
    mock_sql_repo.read_course_by_name.return_value = None
    mock_sql_repo.create_course.return_value = "course-1"
    mock_vector_repo.create_collection.side_effect = Exception("Vector init failed")

    with pytest.raises(HTTPException) as exc_info:
        course_service.create_course("inst-1", "CS101", "ISU", 1, 2025)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    mock_sql_repo.delete_course.assert_called_once_with("course-1")


def test_read_course_success(course_service: CourseService, mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_course.return_value = {"id": "c1", "name": "CS101"}

    result = course_service.read_course("c1")

    assert result["name"] == "CS101"
    mock_sql_repo.read_course.assert_called_once_with("c1")


def test_read_course_not_found(course_service: CourseService, mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_course.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        course_service.read_course("fake")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_read_all_courses(course_service: CourseService, mock_sql_repo: ISQLRepository):
    mock_sql_repo.read_all_courses.return_value = [{"name": "CS101"}, {"name": "CS102"}]

    result = course_service.read_all_courses(institution="Iowa")

    assert len(result) == 2
    mock_sql_repo.read_all_courses.assert_called_once()


def test_delete_course_success(course_service: CourseService, mock_sql_repo: ISQLRepository, mock_vector_repo: IVectorRepository):
    mock_sql_repo.read_course.return_value = {"id": "c1"}

    result = course_service.delete_course("c1")

    mock_sql_repo.delete_course.assert_called_once_with("c1")
    mock_vector_repo.delete_collection.assert_called_once_with("c1")
    assert result == {"status": "deleted", "course_id": "c1"}


def test_delete_course_not_found(course_service: CourseService, mock_sql_repo: ISQLRepository, mock_vector_repo: IVectorRepository):
    mock_sql_repo.read_course.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        course_service.delete_course("fake")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

def test_get_course_id_by_name_success(course_service: CourseService, mock_sql_repo: ISQLRepository):
    """Should return course_id if course exists."""
    mock_sql_repo.get_course_by_name.return_value = {"id": "course-123"}

    result = course_service.get_course_id_by_name("CS101")

    mock_sql_repo.get_course_by_name.assert_called_once_with("CS101")
    assert result == {"course_id": "course-123"}


def test_get_course_id_by_name_not_found(course_service: CourseService, mock_sql_repo: ISQLRepository):
    """Should raise 404 if course name not found."""
    mock_sql_repo.get_course_by_name.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        course_service.get_course_id_by_name("UnknownCourse")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
