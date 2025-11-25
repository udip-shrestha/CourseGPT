from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException, status
from API.Service.document_service import DocumentService
from API.Service.rag_service import RAGService
from API.Repository.i_sql_repository import ISQLRepository


def test_create_document_success(document_service: DocumentService, mock_sql_repo: ISQLRepository, mock_rag_service: RAGService) -> None:
    """Should successfully create a new document and call RAG indexing."""
    mock_sql_repo.read_file_type_by_mime.return_value = {"id": 1, "extension": "pdf"}
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


def test_create_document_invalid_mime(document_service, mock_sql_repo):
    mock_sql_repo.read_file_type_by_mime.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        document_service.create_document("course-1", "notes.xyz", b"data", "application/xyz")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Unsupported MIME type" in exc_info.value.detail
    mock_sql_repo.create_document.assert_not_called()


def test_vectorize_document_success(document_service, mock_sql_repo, mock_rag_service):
    publish_mock = MagicMock()

    document_service.vectorize_document(
        course_id="c1",
        doc_id="doc-123",
        file_name="a.pdf",
        mime_type="application/pdf",
        file_bytes=b"data",
        publish_to_documents_ws_route=publish_mock,
    )

    mock_rag_service.create_index.assert_called_once_with("c1", "doc-123", "a.pdf", "application/pdf", b"data")
    mock_sql_repo.update_document_processing_status_completed.assert_called_once_with("doc-123")

    publish_mock.assert_called_once_with({
        "event": "processing_status_changed",
        "doc_id": "doc-123",
        "status": "COMPLETED",
    })


def test_vectorize_document_failure(document_service, mock_sql_repo, mock_rag_service):
    publish_mock = MagicMock()
    mock_rag_service.create_index.side_effect = Exception("Index error")

    document_service.vectorize_document(
        course_id="c1",
        doc_id="doc-123",
        file_name="a.pdf",
        mime_type="application/pdf",
        file_bytes=b"data",
        publish_to_documents_ws_route=publish_mock,
    )

    mock_rag_service.create_index.assert_called_once()
    mock_sql_repo.update_document_processing_status_failed.assert_called_once_with("doc-123")

    publish_mock.assert_called_once_with({
        "event": "processing_status_changed",
        "doc_id": "doc-123",
        "status": "FAILED",
    })


def test_read_document_success(document_service, mock_sql_repo):
    mock_sql_repo.read_document.return_value = {
        "id": "doc-1", "course_id": "c1", "file_name": "hw1.pdf",
        "file_data": b"x", "mime_type": "application/pdf",
        "can_preview": True, "native_preview": True,
    }

    doc = document_service.read_document("c1", "doc-1")

    mock_sql_repo.read_document.assert_called_once_with("c1", "doc-1")
    assert doc["id"] == "doc-1"
    assert doc["file_name"] == "hw1.pdf"


def test_read_document_not_found(document_service, mock_sql_repo):
    mock_sql_repo.read_document.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        document_service.read_document("c1", "missing")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail.lower()


def test_read_document_wrong_course(document_service: DocumentService, mock_sql_repo: ISQLRepository) -> None:
    """Should raise 404 if document doesn't belong to this course (filtered in SQL)."""
    mock_sql_repo.read_document.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        document_service.read_document("expected-course", "doc-1")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail.lower()
    mock_sql_repo.read_document.assert_called_once_with("expected-course", "doc-1")


def test_read_all_documents(document_service, mock_sql_repo):
    mock_sql_repo.read_all_documents.return_value = {
        "total": 2,
        "documents": [
            {"file_name": "a.pdf", "uploaded_at": "2025-10-15"},
            {"file_name": "b.pdf", "uploaded_at": "2025-10-14"},
        ]
    }

    docs = document_service.read_all_documents("course-1")

    mock_sql_repo.read_all_documents.assert_called_once()
    assert docs["total"] == 2
    assert len(docs["documents"]) == 2
    assert docs["documents"][0]["uploaded_at"] >= docs["documents"][1]["uploaded_at"]


def test_delete_document(document_service, mock_sql_repo, mock_rag_service):
    response = document_service.delete_document("course-1", "doc-1")

    mock_sql_repo.delete_document.assert_called_once_with("course-1", "doc-1")
    mock_rag_service.delete_index.assert_called_once_with("course-1", "doc-1")

    assert response == {"status": "deleted", "course_id": "course-1", "doc_id": "doc-1"}


def test_delete_document_idempotent(document_service, mock_sql_repo, mock_rag_service):
    response = document_service.delete_document("course-1", "nonexistent-id")

    mock_sql_repo.delete_document.assert_called_once_with("course-1", "nonexistent-id")
    mock_rag_service.delete_index.assert_called_once_with("course-1", "nonexistent-id")

    assert response == {"status": "deleted", "course_id": "course-1", "doc_id": "nonexistent-id"}


def test_download_document_success(document_service, mock_sql_repo):
    """Should return filename, bytes, and mime_type."""
    mock_sql_repo.read_document.return_value = {
        "file_name": "notes.pdf",
        "file_data": b"hello",
        "mime_type": "application/pdf"
    }

    file_name, file_bytes, mime_type = document_service.download_document("course-1", "doc-1")

    mock_sql_repo.read_document.assert_called_once_with("course-1", "doc-1")
    assert file_name == "notes.pdf"
    assert file_bytes == b"hello"
    assert mime_type == "application/pdf"


def test_preview_document_native(document_service, mock_sql_repo):
    """If native_preview=True, return original MIME type."""
    mock_sql_repo.read_document.return_value = {
        "file_name": "notes.pdf",
        "file_data": b"hello",
        "mime_type": "application/pdf",
        "can_preview": True,
        "native_preview": True,
    }

    file_name, file_bytes, mime_type = document_service.preview_document("course-1", "doc-1")

    assert file_name == "notes.pdf"
    assert file_bytes == b"hello"
    assert mime_type == "application/pdf"


def test_preview_document_non_native(document_service, mock_sql_repo):
    """If native_preview=False, return text/plain."""
    mock_sql_repo.read_document.return_value = {
        "file_name": "slide.pptx",
        "file_data": b"binary",
        "mime_type": "application/vnd.ms-powerpoint",
        "can_preview": True,
        "native_preview": False,
    }

    file_name, file_bytes, mime_type = document_service.preview_document("course-1", "doc-1")

    assert mime_type == "text/plain"
    assert file_name == "slide.pptx"
    assert file_bytes == b"binary"


def test_preview_document_not_allowed(document_service, mock_sql_repo):
    """Should raise 400 if can_preview=False."""
    mock_sql_repo.read_document.return_value = {
        "file_name": "data.bin",
        "file_data": b"xxxx",
        "mime_type": "application/octet-stream",
        "can_preview": False,
        "native_preview": False,
    }

    with pytest.raises(HTTPException) as exc:
        document_service.preview_document("course-1", "doc-1")

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Preview not supported" in exc.value.detail


def test_preview_document_not_allowed(document_service, mock_sql_repo):
    """Should raise 400 if can_preview=False."""
    mock_sql_repo.read_document.return_value = {
        "file_name": "data.bin",
        "file_data": b"xxxx",
        "mime_type": "application/octet-stream",
        "can_preview": False,
        "native_preview": False,
    }

    with pytest.raises(HTTPException) as exc:
        document_service.preview_document("course-1", "doc-1")

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Preview not supported" in exc.value.detail


def test_preview_document_not_found(document_service, mock_sql_repo):
    mock_sql_repo.read_document.return_value = None

    with pytest.raises(HTTPException) as exc:
        document_service.preview_document("course-1", "missing")

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
