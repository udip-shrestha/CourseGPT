import pytest
from fastapi import HTTPException, status
from API.Service.document_service import DocumentService


def test_create_document_success(document_service: DocumentService):
    """Should successfully create a new document."""
    course_id = document_service.sql_repo.courses[0]["id"]

    result = document_service.create_document(
        course_id=course_id,
        file_name="lecture1.pdf",
        file_bytes=b"fake-binary",
        mime_type="application/pdf",
    )

    # Assertions
    assert "doc_id" in result
    doc = document_service.sql_repo.read_document(result["doc_id"])
    assert doc is not None
    assert doc["file_name"] == "lecture1.pdf"
    assert doc["course_id"] == course_id


def test_create_document_invalid_mime(document_service: DocumentService):
    """Should raise 400 for unsupported MIME type."""
    course_id = document_service.sql_repo.courses[0]["id"]

    with pytest.raises(HTTPException) as exc_info:
        document_service.create_document(
            course_id=course_id,
            file_name="notes.xyz",
            file_bytes=b"data",
            mime_type="application/xyz"
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Unsupported MIME type" in exc_info.value.detail


def test_read_document_success(document_service: DocumentService):
    """Should read an existing document."""
    repo = document_service.sql_repo
    course_id = repo.courses[0]["id"]

    doc_id = repo.create_document(course_id, "hw1.pdf", b"binary", 1)
    doc = document_service.read_document(course_id, doc_id)

    assert doc["id"] == doc_id
    assert doc["file_name"] == "hw1.pdf"


def test_read_document_not_found(document_service: DocumentService):
    """Should raise 404 for non-existent document."""
    with pytest.raises(HTTPException) as exc_info:
        document_service.read_document("some-course-id", "some-document-id")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail.lower()


def test_read_document_wrong_course(document_service: DocumentService):
    """Should raise 404 if document exists but belongs to a different course."""
    repo = document_service.sql_repo

    course_a = repo.courses[0]["id"]
    course_b = repo.courses[1]["id"]

    doc_id = repo.create_document(course_a, "hw1.pdf", b"binary", 1)

    with pytest.raises(HTTPException) as exc_info:
        document_service.read_document(course_b, doc_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail.lower()


def test_read_all_documents(document_service: DocumentService):
    """Should return paginated documents list."""
    repo = document_service.sql_repo
    course_id = repo.courses[0]["id"]

    repo.create_document(course_id, "a.pdf", b"a", 1)
    repo.create_document(course_id, "b.pdf", b"b", 1)

    docs = document_service.read_all_documents(course_id=course_id)

    assert len(docs) == 2
    assert all("file_name" in d for d in docs)
    assert docs[0]["uploaded_at"] >= docs[1]["uploaded_at"]  # sorted DESC by default


def test_delete_document(document_service: DocumentService):
    """Should delete a document successfully."""
    repo = document_service.sql_repo
    course_id = repo.courses[0]["id"]
    doc_id = repo.create_document(course_id, "temp.pdf", b"temp", 1)

    response = document_service.delete_document(course_id, doc_id)
    assert response == {"status": "deleted", "course_id": course_id, "doc_id": doc_id}

    assert repo.read_document(doc_id) is None


def test_delete_document_idempotent(document_service: DocumentService):
    """Deleting a non-existing document should be a no-op (SQL-like behavior)."""
    course_id = document_service.sql_repo.courses[0]["id"]
    response = document_service.delete_document(course_id, "nonexistent-id")

    assert response["status"] == "deleted"
    assert response["doc_id"] == "nonexistent-id"
