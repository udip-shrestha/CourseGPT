from fastapi import APIRouter, UploadFile, File, Query, Depends, status, Path
from typing import Optional
from langchain_core.documents import Document
from API.Service.document_service import DocumentService
from API.dependencies import authorize_course, get_document_service

router = APIRouter(tags=["Documents"])

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
async def upload_document(
    course_id: str = Path(
        ...,
        description="UUID of the course (e.g., the 'Data Structures' course)."
    ),
    file: UploadFile = File(
        ...,
        description="Select a file to upload, e.g., `Backend_Knowledge.pdf` (application/pdf)."
    ),
    _auth: dict = Depends(authorize_course),
    service: DocumentService = Depends(get_document_service)
):
    content = await file.read()
    return service.create_document(
        course_id=course_id,
        file_name=file.filename,
        file_bytes=content,
        mime_type=file.content_type
    )


@router.get(
    "/courses/{course_id}/documents/{doc_id}",
    status_code=status.HTTP_200_OK,
    summary="Retrieve a document by ID",
    description=(
        "**Action:** Fetches a document’s metadata and stored file data by its unique ID.\n\n"
        "**Returns:** The document record including filename, MIME type, and timestamps."
    ),
)
def get_document(
    course_id: str = Path(
        ..., 
        description="UUID of the course that owns the document."
    ),
    doc_id: str = Path(
        ...,
        description="UUID of the document, e.g., the uploaded 'Backend_Knowledge.pdf'.",
    ),
    _auth: dict = Depends(authorize_course),
    service: DocumentService = Depends(get_document_service),
):
    """Fetch a specific document record by ID (validated against course_id)."""
    return service.read_document(course_id, doc_id)


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
    ),
    file_type: Optional[str] = Query(
        None,
        description="Optional MIME type to filter by (e.g., `application/pdf`, `text/plain`).",
        example="application/pdf",
    ),
    limit: int = Query(
        10,
        ge=1,
        description="Maximum number of results to return per page (must be ≥ 1).",
        example=10,
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Starting index for pagination (must be ≥ 0).",
        example=0,
    ),
    order_by: str = Query(
        "uploaded_at",
        description="Field name to sort results by (e.g., `uploaded_at`, `file_name`).",
        example="uploaded_at",
    ),
    order_dir: str = Query(
        "desc",
        description="Sorting direction for results. Must be either `'asc'` or `'desc'`.",
        example="desc",
        regex="^(asc|desc)$",  # only allow these two values
    ),
    _auth: dict = Depends(authorize_course),
    service: DocumentService = Depends(get_document_service),
):
    """Retrieve all documents with optional filters and pagination."""
    return service.read_all_documents(
        course_id=course_id,
        file_type=file_type,
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
    ),
    doc_id: str = Path(
        ...,
        description="UUID of the document to delete.",
    ),
    _auth: dict = Depends(authorize_course),
    service: DocumentService = Depends(get_document_service),
):
    """Deletes a document from the system."""
    return service.delete_document(course_id, doc_id)

