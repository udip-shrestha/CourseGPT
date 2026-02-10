import pytest
from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from io import BytesIO

from starlette.status import HTTP_404_NOT_FOUND

from API.Routers.documents_router import router as documents_router
from API.Service.document_service import DocumentService


@pytest.fixture
def mock_document_service() -> DocumentService:
    """Provides a mocked DocumentService instance."""
    return MagicMock(spec=DocumentService)


@pytest.fixture
def capture_background_tasks(monkeypatch):
    scheduled_tasks = []

    def fake_add_task(self, func, *args, **kwargs):
        scheduled_tasks.append((func, args, kwargs))

    monkeypatch.setattr(BackgroundTasks, "add_task", fake_add_task)

    return scheduled_tasks


@pytest.fixture
def mock_ws_manager():
    manager = MagicMock()

    async def fake_handle_subscription(topic, websocket):
        await websocket.accept()

    manager.handle_subscription = AsyncMock(side_effect=fake_handle_subscription)
    manager.publish = MagicMock()

    return manager


@pytest.fixture
def client(mock_document_service: DocumentService, mock_ws_manager) -> TestClient:
    """Creates a test client with dependency overrides."""
    from API.dependencies import get_document_service, authorize_course, validate_course, get_web_socket_manager

    app = FastAPI()
    app.include_router(documents_router)

    # Override dependencies
    app.dependency_overrides[get_document_service] = lambda: mock_document_service
    app.dependency_overrides[authorize_course] = lambda: {"user": "mock-user"}  # fake auth
    app.dependency_overrides[validate_course] = lambda: {"id": "course-1"}  
    app.dependency_overrides[get_web_socket_manager] = lambda: mock_ws_manager

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


def test_upload_document_uses_background_tasks_and_web_socket_manager_publish(
    client,
    mock_document_service,
    mock_ws_manager,
    capture_background_tasks,
):
    scheduled_tasks = capture_background_tasks

    mock_document_service.create_document.return_value = {"doc_id": "doc-123"}

    file_bytes = b"hello world"
    file_obj = BytesIO(file_bytes)

    response = client.post(
        "/courses/course-1/documents",
        files={"file": ("Doc.pdf", file_obj, "application/pdf")}
    )

    assert response.status_code == 201

    # One background task was scheduled
    assert len(scheduled_tasks) == 1

    func, args, kwargs = scheduled_tasks[0]

    assert func == mock_document_service.vectorize_document

    assert args[0] == "course-1"
    assert args[1] == "doc-123"
    assert args[2] == "Doc.pdf"
    assert args[3] == "application/pdf"
    assert args[4] == file_bytes

    callback = args[5]
    assert callable(callback)

    callback({"done": True})

    mock_ws_manager.publish.assert_called_once_with(
        "/courses/course-1/documents",
        {"done": True}
    )


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


def test_websocket_subscribe_to_course_documents(client: TestClient, mock_ws_manager):
    with client.websocket_connect("/courses/course-1/documents") as ws:
        assert ws is not None
        ws.close()

    mock_ws_manager.handle_subscription.assert_called_once()

    topic, websocket = mock_ws_manager.handle_subscription.call_args[0]

    assert topic == "/courses/course-1/documents"
    assert hasattr(websocket, "send_text")
    assert hasattr(websocket, "accept")
