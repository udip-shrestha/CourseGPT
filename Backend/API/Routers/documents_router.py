from io import BytesIO
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Query, Depends, WebSocket, status, Path
from fastapi.responses import StreamingResponse

from API.Service.document_service import DocumentService
from API.dependencies import authorize_course, get_document_service, get_web_socket_manager, validate_course
from API.Util.web_socket_manager import WebSocketManager


router = APIRouter(tags=["Documents"])


COURSE_DOCUMENTS_WS_ROUTE = "/courses/{course_id}/documents"


@router.post(
    "/courses/{course_id}/documents",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new course document",
    description=(
        "**Action:** Uploads a new document (PDF, DOCX, TXT, etc.) to a specific course. "
        "The uploaded file is read into memory and persisted in the database.\n\n"
        "**Returns:** JSON containing the created document's ID."
    ),
)
def upload_document(
    background_tasks: BackgroundTasks,
    course_id: str = Path(
        ...,
        description="UUID of the course (e.g., the 'Data Structures' course).",
    ),
    file: UploadFile = File(
        ...,
        description="Select a file to upload, e.g., `Backend_Knowledge.pdf` (application/pdf).",
    ),
    _auth: dict = Depends(authorize_course),
    service: DocumentService = Depends(get_document_service),
    ws_manager: WebSocketManager = Depends(get_web_socket_manager),
):
    """Uploads a new document for a specific course."""
    content = file.file.read()
    doc = service.create_document(course_id=course_id, file_name=file.filename, file_bytes=content, mime_type=file.content_type)

    background_tasks.add_task(
        service.vectorize_document,
        course_id,
        doc["doc_id"],
        file.filename,
        file.content_type,
        content,
        lambda payload: ws_manager.publish(COURSE_DOCUMENTS_WS_ROUTE.format(course_id=course_id), payload)
    )

    return doc


@router.get(
    "/courses/{course_id}/documents",
    status_code=status.HTTP_200_OK,
    summary="List all documents with optional filters",
    description=(
        "**Action:** Retrieves a paginated list of uploaded documents. "
        "Supports filtering by course ID and MIME type, and allows sorting and pagination.\n\n"
        "**Returns:** A JSON array of document metadata objects (ID, filename, MIME type, timestamps, etc.)."
    ),
)
def get_all_documents(
    course_id: str = Path(
        ...,
        description="UUID of the course.",
        examples={"example": "8b7e9f2a-d4a1-4e5c-94b9-3c6f4ab0e9cd"},
    ),
    mime_type: Optional[str] = Query(
        None,
        description="Optional MIME type to filter by (e.g., `application/pdf`, `text/plain`).",
        examples={"example": "application/pdf"},
    ),
    file_name: Optional[str] = Query(
        None,
        description="Optional substring to filter file names (case-insensitive).",
        examples={"example": "chapter"},
    ),
    limit: int = Query(
        10,
        ge=1,
        description="Maximum number of results to return per page (must be ≥ 1).",
        examples={"example": 10},
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Starting index for pagination (must be ≥ 0).",
        examples={"example": 0},
    ),
    order_by: str = Query(
        "uploaded_at",
        description="Field name to sort results by (e.g., `uploaded_at`, `file_name`).",
        examples={"example": "uploaded_at"},
    ),
    order_dir: str = Query(
        "desc",
        description="Sorting direction for results. Must be either `'asc'` or `'desc'`.",
        examples={"example": "desc"},
        pattern="^(asc|desc)$",
    ),
    _auth: dict = Depends(authorize_course),
    service: DocumentService = Depends(get_document_service),
):
    """Retrieve all documents with optional filters and pagination."""
    return service.read_all_documents(
        course_id=course_id,
        mime_type=mime_type,
        file_name=file_name,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_dir=order_dir,
    )


@router.delete(
    "/courses/{course_id}/documents/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document by course and ID",
    description=(
        "**Action:** Permanently deletes a document associated with a specific course. "
        "Removes both metadata and binary file data from the database.\n\n"
        "**Returns:** 204 No Content on successful deletion."
    ),
)
def delete_document(
    course_id: str = Path(
        ...,
        description="UUID of the course that owns the document.",
        examples={"example": "8b7e9f2a-d4a1-4e5c-94b9-3c6f4ab0e9cd"},
    ),
    doc_id: str = Path(
        ...,
        description="UUID of the document to delete.",
        examples={"example": "3f9aab52-ef01-4a11-9a3d-1115a6ecf83b"},
    ),
    _auth: dict = Depends(authorize_course),
    service: DocumentService = Depends(get_document_service),
):
    """Deletes a document from the system."""
    return service.delete_document(course_id, doc_id)


@router.get(
    "/courses/{course_id}/documents/{doc_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Download a document as a file attachment",
    description=(
        "**Action:** Streams the binary file associated with a specific document ID so "
        "the client can download it directly.\n\n"
        "**Behavior:** Returns the file as an attachment using the appropriate "
        "`Content-Disposition` header. Browsers will prompt the user to save the file "
        "with the original filename and MIME type.\n\n"
        "**Returns:** A streamed binary file (PDF, DOCX, TXT, etc.) with accurate "
        "MIME type and filename."
    ),
)
def download_document(
    course_id: str = Path(
        ...,
        description="UUID of the course that owns the document.",
        examples={"example": "8b7e9f2a-d4a1-4e5c-94b9-3c6f4ab0e9cd"},
    ),
    doc_id: str = Path(
        ...,
        description="UUID of the document to download.",
        examples={"example": "3f9aab52-ef01-4a11-9a3d-1115a6ecf83b"},
    ),
    _auth: dict = Depends(authorize_course),
    service: DocumentService = Depends(get_document_service),
):
    """
    Streams the binary file associated with a document so it can be downloaded
    by the client as a file attachment.
    """
    # Fetch document metadata + raw bytes
    doc = service.read_document(course_id, doc_id)
    return StreamingResponse(
        BytesIO(doc["file_data"]),
        media_type=doc["mime_type"],
        headers={
            # MUST include both for Chrome/Firefox/Safari compatibility
            "Content-Disposition": f'attachment; filename="{doc["file_name"]}"; filename*=UTF-8\'\'{doc["file_name"]}',
        },
    )


@router.get(
    "/courses/{course_id}/documents/{doc_id}/preview",
    status_code=status.HTTP_200_OK,
    summary="Preview a document inline in the browser",
    description=(
        "**Action:** Streams the binary document for inline browser preview. "
        "This is typically used for PDFs, images, and other formats your browser can render.\n\n"
        "**Behavior:** Sends the file using the `inline` Content-Disposition header, allowing the "
        "browser to display the document directly in a new tab. If the browser cannot render the "
        "file type, it may fallback to prompting the user to download.\n\n"
        "**Returns:** A streamed binary response using the correct MIME type (e.g., "
        "`application/pdf`, `image/png`, `text/plain`)."
    ),
)
def preview_document(
    course_id: str = Path(
        ...,
        description="UUID of the course that owns the document.",
        examples={"example": "8b7e9f2a-d4a1-4e5c-94b9-3c6f4ab0e9cd"},
    ),
    doc_id: str = Path(
        ...,
        description="UUID of the document to preview.",
        examples={"example": "3f9aab52-ef01-4a11-9a3d-1115a6ecf83b"},
    ),
    _auth: dict = Depends(authorize_course),
    service: DocumentService = Depends(get_document_service),
):
    """
    Streams the binary file associated with a document so it can be displayed
    by the browser inline (for example, PDFs or images).
    """
    file_name, file_bytes, mime_type = service.preview_document(course_id, doc_id)
    return StreamingResponse(
        BytesIO(file_bytes),
        media_type=mime_type,
        headers={
            "Content-Disposition": f'inline; filename="{file_name}"; filename*=UTF-8\'\'{file_name}'
        },
    )

@router.websocket(COURSE_DOCUMENTS_WS_ROUTE)
async def subscribe_to_course_queries(
    websocket: WebSocket,
    _course: dict = Depends(validate_course),
    manager: WebSocketManager = Depends(get_web_socket_manager),
):
    """
    WebSocket endpoint for subscribing to real-time query updates for a course.
    """
    await manager.handle_subscription(websocket.url.path, websocket)
