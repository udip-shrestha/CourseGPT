import base64
import pytest
import uuid
from API.Repository.i_sql_repository import ISQLRepository

# ==========================================================
# FILE TYPES
# ==========================================================
def test_read_file_type_by_mime(repo):
    result = repo.read_file_type_by_mime("application/pdf")
    assert result is not None
    assert result["mime_type"] == "application/pdf"
    assert result["extension"] == "pdf"


def test_read_file_type_by_extension(repo):
    result = repo.read_file_type_by_extension("txt")
    assert result is not None
    assert result["extension"] == "txt"
    assert result["mime_type"] == "text/plain"


def test_read_all_file_types(repo):
    result = repo.read_all_file_types()
    assert isinstance(result, list)
    assert len(result) >= 2
    mime_types = [r["mime_type"] for r in result]
    assert "application/pdf" in mime_types
    assert "text/plain" in mime_types


# ==========================================================
# DOCUMENTS
# ==========================================================
def test_create_and_read_document(repo, temp_course):
    # Arrange
    file_name = "lecture1.pdf"
    file_bytes = b"dummy data"
    file_type_id = 1  # assuming 'application/pdf' has ID=1 from seed data

    # Act
    doc_id = repo.create_document(temp_course, file_name, file_bytes, file_type_id)
    assert doc_id is not None

    # Read it back
    doc = repo.read_document(temp_course, doc_id)
    assert doc is not None
    assert doc["course_id"] == uuid.UUID(temp_course)
    assert doc["file_name"] == file_name
    assert base64.b64decode(doc["file_data"]) == file_bytes


def test_read_all_documents_filters_and_pagination(repo, temp_course):
    # Insert multiple documents for pagination
    for i in range(3):
        repo.create_document(
            temp_course, f"file_{i}.pdf", b"data" + bytes([i]), file_type_id=1
        )

    results = repo.read_all_documents(course_id=temp_course, limit=2, offset=0)
    assert len(results["documents"]) == 2

    results_next = repo.read_all_documents(course_id=temp_course, limit=2, offset=2)
    assert isinstance(results_next["documents"], list)


def test_delete_document(repo, temp_course):
    doc_id = repo.create_document(temp_course, "temp.txt", b"hello", file_type_id=2)
    assert repo.read_document(temp_course, doc_id) is not None

    repo.delete_document(course_id=temp_course, doc_id=doc_id)
    assert repo.read_document(temp_course, doc_id) is None



# ==========================================================
# INSTRUCTORS
# ==========================================================
def test_create_instructor(repo: ISQLRepository):
    """Should create instructor and handle duplicate/invalid edge cases."""
    instructor_id = repo.create_instructor("Dr. Jane Smith", "Professor", "ISU", "jane.smith@isu.edu", "fake-hash")
    assert instructor_id is not None

    # Duplicate email should raise
    with pytest.raises(Exception):
        repo.create_instructor("Dr. Copy", "Professor", "ISU", "jane.smith@isu.edu", "hash2")

    # Empty fields might be allowed by schema, so no exception expected
    repo.create_instructor("", "", "", "unique@example.com", "pw")

def test_read_instructor(repo: ISQLRepository):
    """Should fetch instructors by ID/email and handle not-found cases."""
    instructor_id = repo.create_instructor("Dr. Jane Smith", "Professor", "ISU", "jane.smith@isu.edu", "fake-hash")

    # By ID 
    instructor = repo.read_instructor(instructor_id)
    assert instructor is not None
    assert instructor["name"] == "Dr. Jane Smith"
    assert instructor["role"] == "INSTRUCTOR"

    # By Email
    found = repo.read_instructor_by_email("jane.smith@isu.edu")
    assert found is not None
    assert found["email"] == "jane.smith@isu.edu"

    # Nonexistent
    assert repo.read_instructor("00000000-0000-0000-0000-000000000000") is None
    assert repo.read_instructor_by_email("notfound@isu.edu") is None


def test_read_all_instructors_features(repo: ISQLRepository, temp_instructor: str):
    """Should support filtering, ordering, and pagination."""
    result = repo.read_all_instructors()
    instructors = result["instructors"]
    assert isinstance(instructors, list)
    if instructors:
        assert "email" in instructors[0] and "role" in instructors[0]

    filtered = repo.read_all_instructors(role="INSTRUCTOR")["instructors"]
    assert all(inst["role"] == "INSTRUCTOR" for inst in filtered)

    limited = repo.read_all_instructors(limit=1)["instructors"]
    assert len(limited) <= 1

    invalid = repo.read_all_instructors(order_by="invalid_field")["instructors"]
    assert isinstance(invalid, list)



# ==========================================================
# COURSES
# ==========================================================
def test_create_and_read_course(repo, temp_instructor):
    course_id = repo.create_course(
        name="Test Course",
        institution="ISU",
        year=2025,
        semester_id=1,
        instructor_id=temp_instructor,
    )
    assert course_id is not None

    course = repo.read_course(course_id)
    assert course is not None
    assert course["name"] == "Test Course"


def test_read_all_courses(repo):
    results = repo.read_all_courses()["courses"]
    assert isinstance(results, list)


def test_delete_course(repo, temp_instructor):
    course_id = repo.create_course(
        name="Temp Course", institution="ISU", year=2025, semester_id=1, instructor_id=temp_instructor
    )
    repo.delete_course(course_id)
    assert repo.read_course(course_id) is None
