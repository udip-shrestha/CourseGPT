import pytest
from fastapi import HTTPException, status
from API.Service.document_service import DocumentService
from API.Repository.i_sql_repository import ISQLRepository


def test_create_document_success(document_service: DocumentService, mock_sql_repo: ISQLRepository):
    """Should successfully create a new document."""
    mock_sql_repo.read_file_type_by_mime.return_value = {"id": 1}
    mock_sql_repo.create_document.return_value = "doc-123"

    result = document_service.create_document(
        course_id="course-1",
        file_name="lecture1.pdf",
        file_bytes=b"fake-binary",
        mime_type="application/pdf",
    )

    mock_sql_repo.read_file_type_by_mime.assert_called_once_with("application/pdf")
    mock_sql_repo.create_document.assert_called_once_with("course-1", "lecture1.pdf", b"fake-binary", 1)
    assert result == {"doc_id": "doc-123"}


def test_create_document_invalid_mime(document_service: DocumentService, mock_sql_repo: ISQLRepository):
    """Should raise 400 for unsupported MIME type."""
    mock_sql_repo.read_file_type_by_mime.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        document_service.create_document(
            course_id="course-1",
            file_name="notes.xyz",
            file_bytes=b"data",
            mime_type="application/xyz"
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Unsupported MIME type" in exc_info.value.detail
    mock_sql_repo.create_document.assert_not_called()


def test_read_document_success(document_service: DocumentService, mock_sql_repo: ISQLRepository):
    """Should read an existing document."""
    mock_sql_repo.read_document.return_value = {"id": "doc-1", "course_id": "c1", "file_name": "hw1.pdf"}

    doc = document_service.read_document("c1", "doc-1")

    mock_sql_repo.read_document.assert_called_once_with("doc-1")
    assert doc["id"] == "doc-1"
    assert doc["file_name"] == "hw1.pdf"


def test_read_document_not_found(document_service: DocumentService, mock_sql_repo: ISQLRepository):
    """Should raise 404 for non-existent document."""
    mock_sql_repo.read_document.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        document_service.read_document("some-course-id", "some-document-id")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail.lower()


def test_read_document_wrong_course(document_service: DocumentService, mock_sql_repo: ISQLRepository):
    """Should raise 404 if document exists but belongs to a different course."""
    mock_sql_repo.read_document.return_value = {"id": "doc-1", "course_id": "wrong-course"}

    with pytest.raises(HTTPException) as exc_info:
        document_service.read_document("expected-course", "doc-1")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail.lower()


def test_read_all_documents(document_service: DocumentService, mock_sql_repo: ISQLRepository):
    """Should return paginated documents list."""
    mock_sql_repo.read_all_documents.return_value = [
        {"file_name": "a.pdf", "uploaded_at": "2025-10-15"},
        {"file_name": "b.pdf", "uploaded_at": "2025-10-14"},
    ]

    docs = document_service.read_all_documents(course_id="course-1")

    mock_sql_repo.read_all_documents.assert_called_once()
    assert len(docs) == 2
    assert all("file_name" in d for d in docs)
    assert docs[0]["uploaded_at"] >= docs[1]["uploaded_at"]


def test_delete_document(document_service: DocumentService, mock_sql_repo: ISQLRepository):
    """Should delete a document successfully."""
    response = document_service.delete_document("course-1", "doc-1")

    mock_sql_repo.delete_document.assert_called_once_with("doc-1")

    assert response == {"status": "deleted", "course_id": "course-1", "doc_id": "doc-1"}


def test_delete_document_idempotent(document_service: DocumentService, mock_sql_repo: ISQLRepository):
    """Deleting a non-existing document should be a no-op (SQL-like behavior)."""
    response = document_service.delete_document("course-1", "nonexistent-id")

    mock_sql_repo.delete_document.assert_called_once_with("nonexistent-id")
    assert response["status"] == "deleted"
    assert response["doc_id"] == "nonexistent-id"
