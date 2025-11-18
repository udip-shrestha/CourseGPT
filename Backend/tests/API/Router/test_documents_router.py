import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from io import BytesIO

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
    args, kwargs = mock_document_service.create_document.call_args
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


def test_get_document_by_id_success(client: TestClient, mock_document_service: DocumentService):
    """Should retrieve a document by its ID."""
    mock_document_service.read_document.return_value = {
        "id": "doc-123",
        "file_name": "Backend_Knowledge.pdf",
        "mime_type": "application/pdf"
    }

    response = client.get("/courses/course-1/documents/doc-123")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == "doc-123"
    mock_document_service.read_document.assert_called_once_with("course-1", "doc-123")


def test_get_document_by_id_not_found(client: TestClient, mock_document_service: DocumentService):
    """Should return 404 if document not found."""
    from fastapi import HTTPException, status

    mock_document_service.read_document.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Document with id=invalid-id not found."
    )

    response = client.get("/courses/course-1/documents/invalid-id")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]


def test_get_all_documents_success(client: TestClient, mock_document_service: DocumentService):
    """Should return a list of documents for a course."""
    mock_document_service.read_all_documents.return_value = [
        {"id": "doc-1", "file_name": "a.pdf", "mime_type": "application/pdf"},
        {"id": "doc-2", "file_name": "b.pdf", "mime_type": "application/pdf"},
    ]

    response = client.get("/courses/course-1/documents")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    mock_document_service.read_all_documents.assert_called_once_with(
        course_id="course-1",
        file_type=None,
        limit=10,
        offset=0,
        order_by="uploaded_at",
        order_dir="desc"
    )


def test_get_all_documents_with_filter(client: TestClient, mock_document_service: DocumentService):
    """Should filter documents by MIME type."""
    mock_document_service.read_all_documents.return_value = [
        {"id": "doc-1", "file_name": "filtered.pdf", "mime_type": "application/pdf"}
    ]

    response = client.get("/courses/course-1/documents", params={"file_type": "application/pdf"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    mock_document_service.read_all_documents.assert_called_once_with(
        course_id="course-1",
        file_type="application/pdf",
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

