import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from io import BytesIO

from starlette.status import HTTP_404_NOT_FOUND

from API.Routers.documents_router import router as documents_router
from API.Service.document_service import DocumentService


@pytest.fixture
def mock_document_service() -> DocumentService:
    """Provides a mocked DocumentService instance."""
    return MagicMock(spec=DocumentService)


@pytest.fixture
def client(mock_document_service: DocumentService) -> TestClient:
    """Creates a test client with dependency overrides."""
    from API.dependencies import get_document_service, authorize_course

    app = FastAPI()
    app.include_router(documents_router)

    # Override dependencies
    app.dependency_overrides[get_document_service] = lambda: mock_document_service
    app.dependency_overrides[authorize_course] = lambda: {"user": "mock-user"}  # fake auth

    return TestClient(app)


def test_upload_document_success(client: TestClient, mock_document_service: DocumentService):
    """Should upload a document and return its ID."""
    mock_document_service.create_document.return_value = {"doc_id": "doc-123"}

    file_data = BytesIO(b"test pdf content")
    response = client.post(
        "/courses/course-1/documents",
        files={"file": ("Backend_Knowledge.pdf", file_data, "application/pdf")}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"doc_id": "doc-123"}
    mock_document_service.create_document.assert_called_once()
    _, kwargs = mock_document_service.create_document.call_args
    
    assert kwargs["course_id"] == "course-1"
    assert kwargs["file_name"] == "Backend_Knowledge.pdf"
    assert kwargs["mime_type"] == "application/pdf"
    assert isinstance(kwargs["file_bytes"], bytes)


def test_upload_document_invalid_file(client: TestClient, mock_document_service: DocumentService):
    """Should handle invalid file upload gracefully."""
    response = client.post(
        "/courses/course-1/documents",
        files={"file": ("", BytesIO(), "application/octet-stream")}
    )
    # Since the file field is required, FastAPI itself should handle this
    assert response.status_code in (status.HTTP_422_UNPROCESSABLE_CONTENT, status.HTTP_400_BAD_REQUEST)
    mock_document_service.create_document.assert_not_called()


def test_get_all_documents_success(client: TestClient, mock_document_service: DocumentService):
    """Should return a list of documents for a course."""
    mock_document_service.read_all_documents.return_value = {
        "total": 2,
        "documents": [
            {"id": "doc-1", "file_name": "a.pdf", "mime_type": "application/pdf"},
            {"id": "doc-2", "file_name": "b.pdf", "mime_type": "application/pdf"},
        ]
    }

    response = client.get("/courses/course-1/documents")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 2
    assert len(data["documents"]) == 2
    mock_document_service.read_all_documents.assert_called_once_with(
        course_id="course-1",
        mime_type=None,
        file_name=None,
        limit=10,
        offset=0,
        order_by="uploaded_at",
        order_dir="desc",
    )


def test_get_all_documents_with_filter(client: TestClient, mock_document_service: DocumentService):
    """Should filter documents by MIME type."""
    mock_document_service.read_all_documents.return_value = {
        "total": 1,
        "documents": [
            {"id": "doc-1", "file_name": "filtered.pdf", "mime_type": "application/pdf"}
        ]
    }

    response = client.get("/courses/course-1/documents", params={"mime_type": "application/pdf"})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert len(data["documents"]) == 1
    mock_document_service.read_all_documents.assert_called_once_with(
        course_id="course-1",
        mime_type="application/pdf",
        file_name=None,
        limit=10,
        offset=0,
        order_by="uploaded_at",
        order_dir="desc"
    )


def test_delete_document_success(client: TestClient, mock_document_service: DocumentService):
    """Should delete a document successfully."""
    mock_document_service.delete_document.return_value = None

    response = client.delete("/courses/course-1/documents/doc-123")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
    mock_document_service.delete_document.assert_called_once_with("course-1", "doc-123")


def test_download_document_success(client, mock_document_service):
    mock_document_service.read_document.return_value = {
        "file_name": "Backend_Knowledge.pdf",
        "file_data": b"hello world",
        "mime_type": "application/pdf",
    }

    response = client.get("/courses/course-1/documents/doc-123/download")

    assert response.status_code == status.HTTP_200_OK
    assert response.content == b"hello world"
    assert response.headers["content-disposition"].startswith("attachment;")

    mock_document_service.read_document.assert_called_once_with("course-1", "doc-123")


def test_download_document_not_found(client, mock_document_service):
    mock_document_service.read_document.side_effect = HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Document not found")

    response = client.get("/courses/course-1/documents/invalid/download")

    assert response.status_code == HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_preview_document_success(client, mock_document_service):
    mock_document_service.preview_document.return_value = (
        "Backend_Knowledge.pdf",
        b"hello world",
        "application/pdf"
    )

    response = client.get("/courses/course-1/documents/doc-123/preview")

    assert response.status_code == status.HTTP_200_OK
    assert response.content == b"hello world"
    assert "inline; filename=" in response.headers["content-disposition"]

    mock_document_service.preview_document.assert_called_once_with("course-1", "doc-123")


def test_preview_document_not_found(client, mock_document_service):
    mock_document_service.preview_document.side_effect = HTTPException(
        status_code=HTTP_404_NOT_FOUND,
        detail="Document not found"
    )

    response = client.get("/courses/course-1/documents/invalid-id/preview")

    assert response.status_code == HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()

    mock_document_service.preview_document.assert_called_once_with("course-1", "invalid-id")

