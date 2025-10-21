import base64
import pytest
import uuid

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
    doc = repo.read_document(doc_id)
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
    assert len(results) == 2

    results_next = repo.read_all_documents(course_id=temp_course, limit=2, offset=2)
    assert isinstance(results_next, list)


def test_delete_document(repo, temp_course):
    doc_id = repo.create_document(temp_course, "temp.txt", b"hello", file_type_id=2)
    assert repo.read_document(doc_id) is not None

    # Delete it
    repo.delete_document(doc_id)
    assert repo.read_document(doc_id) is None

# ==========================================================
# INSTRUCTORS
# ==========================================================
def test_create_and_read_instructor(repo):
    instructor_id = repo.create_instructor(
        name="Dr. Jane Smith",
        title="Professor",
        university="ISU",
        email="jane.smith@isu.edu",
    )
    assert instructor_id is not None

    instructor = repo.read_instructor(instructor_id)
    assert instructor is not None
    assert instructor["name"] == "Dr. Jane Smith"
    assert instructor["university"] == "ISU"


def test_read_all_instructors(repo, temp_instructor):
    instructors = repo.read_all_instructors()
    assert isinstance(instructors, list)
    assert any(str(inst["id"]) == temp_instructor for inst in instructors)     # Convert UUID to string for comparison

def test_delete_instructor(repo):
    instructor_id = repo.create_instructor(
        name="Dr. Temp", title="Assistant Prof.", university="Test U", email="temp@u.edu"
    )
    repo.delete_instructor(instructor_id)
    deleted = repo.read_instructor(instructor_id)
    assert deleted is None


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
    results = repo.read_all_courses()
    assert isinstance(results, list)


def test_delete_course(repo, temp_instructor):
    course_id = repo.create_course(
        name="Temp Course", institution="ISU", year=2025, semester_id=1, instructor_id=temp_instructor
    )
    repo.delete_course(course_id)
    assert repo.read_course(course_id) is None
