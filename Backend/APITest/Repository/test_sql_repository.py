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
    assert doc["file_data"] == file_bytes


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
