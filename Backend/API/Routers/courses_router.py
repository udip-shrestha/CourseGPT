from fastapi import APIRouter, Query, Depends, status, Path
from API.Service.courses_service import CourseService
from API.dependencies import get_course_service
from typing import Optional

router = APIRouter(tags=["Courses"])

@router.post(
    "/courses/{instructor_id}",
    status_code=status.HTTP_200_OK,
    summary="Add a new course",
    description=(
        "**Action:** Adds a new course to the system. "
        "The uploaded course details is read into memory and persisted in the database.\n\n"
        "**Returns:** JSON containing the created course's ID."
    ),
)

async def add_course(
    instructor_id: str = Path(
        ...,
        description="UUID of the instructor who owns this course (e.g., the professor’s ID)."
    ),
    name: str = Query(
        ...,
        description="Name of the course (e.g., 'Data Structures').",
        example="Data Structures"
    ),
    institution: str = Query(
        ...,
        description="Name of the institution offering the course.",
        example="Iowa State University"
    ),
    semester_id: int = Query(
        ...,
        description="Numeric ID of the semester (e.g., 3 = Fall).",
        example=3
    ),
    year: int = Query(
        ...,
        description="Academic year when the course is offered.",
        example=2025
    ),
    service: CourseService = Depends(get_course_service)
):
    """Creates a new course record associated with a specific instructor."""
    return service.create_course(
        instructor_id=instructor_id,
        name=name,
        institution=institution,
        semester_id=semester_id,
        year=year
    )

@router.get(
    "/instructors/{instructor_id}/courses",
    status_code=status.HTTP_200_OK,
    summary="Get a list of courses taught by an instructor",
    description=(
        "**Action:** Gets a list of courses taught by an instructor. "
        "Supports filtering by institution, sorting, and pagination.\n\n"
        "**Returns:** A JSON array of course metadata objects (ID, courseName, semester, timestamps, etc.)."
    ),
)
def get_all_courses(
    instructor_id: str = Path(
        ...,
        description="UUID of the instructor.",
        example="69898770-08e8-4491-a0b1-640f23168397"
    ),
    institution: Optional[str] = Query(
        None,
        description="Optional filter by institution name.",
        example="Iowa State University"
    ),
    limit: int = Query(
        10,
        ge=1,
        description="Maximum number of results to return per page (must be ≥ 1).",
        example=10
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Starting index for pagination (must be ≥ 0).",
        example=0
    ),
    order_by: str = Query(
        "created_at",
        description="Field name to sort results by (e.g., `year`, `created_at`).",
        example="created_at"
    ),
    order_dir: str = Query(
        "desc",
        description="Sorting direction for results (`asc` or `desc`).",
        example="desc",
        regex="^(asc|desc)$"
    ),
    service: CourseService = Depends(get_course_service)
):
    """Retrieve all courses with optional filtering and pagination."""
    return service.read_all_courses(
        instructor_id=instructor_id,
        institution=institution,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_dir=order_dir
    )


@router.delete(
    "/courses/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a course by ID",
    description=(
        "**Action:** Permanently deletes a course record from the database.\n\n"
        "**Returns:** 204 No Content on success."
    ),
)
def delete_course(
    course_id: str = Path(
        ...,
        description="UUID of the course to delete."
    ),
    service: CourseService = Depends(get_course_service),
):
    """Deletes a course from the system."""
    return service.delete_course(course_id)