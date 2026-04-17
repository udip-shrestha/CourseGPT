from fastapi import APIRouter, Query, Depends, status, Path
from API.Service.instructors_service import InstructorService
from API.dependencies import get_instructor_service
from Metrics.metrics import MetricsRoute
from typing import Optional


router = APIRouter(tags=["Instructors"], route_class=MetricsRoute)


@router.get(
    "/instructors/{instructor_id}",
    status_code=status.HTTP_200_OK,
    summary="Get an instructor by ID",
    description="Fetch a single instructor by their UUID.",
)
def get_instructor(
    instructor_id: str = Path(
        ...,
        description="UUID of the instructor.",
        examples={"example": "5f3c1b56-8a2e-4f81-9f43-3a6a5dfb5b1b"},
    ),
    service: InstructorService = Depends(get_instructor_service),
):
    """Retrieve a single instructor by their unique ID."""
    return service.read_instructor(instructor_id)


@router.get(
    "/instructors",
    status_code=status.HTTP_200_OK,
    summary="List all instructors",
    description="Retrieve all instructors with optional university filter and pagination.",
)
def get_all_instructors(
    university: Optional[str] = Query(
        None,
        description="Optional filter by university.",
        examples={"example": "Tech University"},
    ),
    limit: int = Query(
        10,
        ge=1,
        description="Maximum number of results per page.",
        examples={"example": 10},
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Starting index for pagination.",
        examples={"example": 0},
    ),
    order_by: str = Query(
        "created_at",
        description="Field name to sort results.",
        examples={"example": "created_at"},
    ),
    order_dir: str = Query(
        "desc",
        description="Sorting direction (asc/desc).",
        pattern="^(asc|desc)$",
        examples={"example": "desc"},
    ),
    service: InstructorService = Depends(get_instructor_service),
):
    return service.read_all_instructors(university=university, limit=limit, offset=offset, order_by=order_by, order_dir=order_dir)


@router.delete(
    "/instructors/{instructor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an instructor",
    description="Permanently deletes an instructor record.",
)
def delete_instructor(
    instructor_id: str = Path(
        ...,
        description="UUID of the instructor to delete.",
        examples={"example": "5f3c1b56-8a2e-4f81-9f43-3a6a5dfb5b1b"},
    ),
    service: InstructorService = Depends(get_instructor_service),
):
    """Deletes an instructor from the system."""
    return service.delete_instructor(instructor_id)


@router.put(
    "/instructors/{instructor_id}",
    status_code=status.HTTP_200_OK,
    summary="Update an instructor",
    description=(
        "**Action:** Updates an instructor's information in the system.\n\n"
        "**Returns:** JSON containing the updated instructor details."
    ),
)
def update_instructor(
    instructor_id: str = Path(
        ...,
        description="UUID of the instructor to update.",
        examples={"example": "5f3c1b56-8a2e-4f81-9f43-3a6a5dfb5b1b"},
    ),
    name: Optional[str] = Query(
        None,
        description="Updated full name of the instructor.",
        examples={"example": "Dr. Sarah Johnson"},
    ),
    title: Optional[str] = Query(
        None,
        description="Updated job title of the instructor.",
        examples={"example": "Associate Professor of Computer Science"},
    ),
    university: Optional[str] = Query(
        None,
        description="Updated university where the instructor works.",
        examples={"example": "Tech University"},
    ),
    email: Optional[str] = Query(
        None,
        description="Updated instructor email address.",
        examples={"example": "sarah.johnson@techuni.edu"},
    ),
    password: Optional[str] = Query(
        None,
        description="Updated password of the instructor.",
        examples={"example": "new-password123"},
    ),
    service: InstructorService = Depends(get_instructor_service),
):
    """Updates an instructor's details."""
    return service.update_instructor(
        instructor_id=instructor_id,
        name=name,
        title=title,
        university=university,
        email=email,
        password=password,
    )

