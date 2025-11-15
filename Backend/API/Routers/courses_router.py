from fastapi import APIRouter, Query, Depends, status, Path
from API.Service.courses_service import CourseService
from API.dependencies import get_course_service
from typing import Optional


router = APIRouter(tags=["Courses"])


@router.post(
    "/instructors/{instructor_id}/courses",
    status_code=status.HTTP_200_OK,
    summary="Add a new course",
    description=(
        "**Action:** Adds a new course to the system. "
        "The uploaded course details are read into memory and persisted in the database.\n\n"
        "**Returns:** JSON containing the created course's ID."
    ),
)
async def add_course(
    instructor_id: str = Path(
        ...,
        description="UUID of the instructor who owns this course (e.g., the professor’s ID).",
    ),
    name: str = Query(
        ...,
        description="Name of the course (e.g., 'Data Structures').",
        examples={"example": "Data Structures"},
    ),
    institution: str = Query(
        ...,
        description="Name of the institution offering the course.",
        examples={"example": "Iowa State University"},
    ),
    semester_id: int = Query(
        ...,
        description="Numeric ID of the semester (e.g., 3 = Fall).",
        examples={"example": 3},
    ),
    year: int = Query(
        ...,
        description="Academic year when the course is offered.",
        examples={"example": 2025},
    ),
    service: CourseService = Depends(get_course_service),
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
        examples={"example": "69898770-08e8-4491-a0b1-640f23168397"},
    ),
    institution: Optional[str] = Query(
        None,
        description="Optional filter by institution name.",
        examples={"example": "Iowa State University"},
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
        "created_at",
        description="Field name to sort results by (e.g., `year`, `created_at`).",
        examples={"example": "created_at"},
    ),
    order_dir: str = Query(
        "desc",
        description="Sorting direction for results (`asc` or `desc`).",
        examples={"example": "desc"},
        pattern="^(asc|desc)$",
    ),
    service: CourseService = Depends(get_course_service),
):
    """Retrieve all courses with optional filtering and pagination."""
    return service.read_all_courses(
        instructor_id=instructor_id,
        institution=institution,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_dir=order_dir,
    )


@router.get(
    "/courses/{course_id}",
    status_code=status.HTTP_200_OK,
    summary="Get course details by ID",
    description=(
        "**Action:** Fetch a single course by its unique ID. "
        "Includes instructor and semester details.\n\n"
        "**Returns:** JSON containing course metadata such as name, institution, "
        "semester, year, instructor info, and timestamps."
    ),
)
def get_course_by_id(
    course_id: str = Path(
        ...,
        description="UUID of the course to retrieve.",
        examples={"example": "a4e7b4a9-8423-4d34-b8b2-4a07f4448dc9"},
    ),
    service: CourseService = Depends(get_course_service),
):
    """Retrieve one course by its unique ID."""
    return service.read_course(course_id)

@router.put(
    "/courses/{course_id}",
    status_code=status.HTTP_200_OK,
    summary="Update an existing course",
    description=(
        "**Action:** Updates course fields (name, institution, semester, or year). "
        "Only provided fields will be updated.\n\n"
        "**Returns:** JSON of the updated course record."
    ),
)
def update_course(
    course_id: str = Path(
        ...,
        description="UUID of the course to update.",
        examples={"example": "a4e7b4a9-8423-4d34-b8b2-4a07f4448dc9"},
    ),
    name: Optional[str] = Query(None, description="Updated course name."),
    institution: Optional[str] = Query(None, description="Updated institution name."),
    semester_id: Optional[int] = Query(None, description="Updated semester ID."),
    year: Optional[int] = Query(None, description="Updated academic year."),
    service: CourseService = Depends(get_course_service),
):
    """Updates one or more fields of a course."""
    updates = {k: v for k, v in {
        "name": name,
        "institution": institution,
        "semester_id": semester_id,
        "year": year
    }.items() if v is not None}

    return service.update_course(course_id, updates)

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
        description="UUID of the course to delete.",
    ),
    service: CourseService = Depends(get_course_service),
):
    """Deletes a course from the system."""
    return service.delete_course(course_id)

@router.get(
    "/courses",
    status_code=status.HTTP_200_OK,
    summary="Get course ID by course name",
    description=(
        "**Action:** Retrieves the unique course ID for a given course name.\n\n"
        "**Returns:** JSON containing the course ID if found."
    ),
)
def get_course_id_by_name(
    course_name: str = Query(
        ...,
        description="Exact name of the course to look up (e.g., 'Data Structures').",
        examples={"example": "Data Structures"},
    ),
    service: CourseService = Depends(get_course_service),
):
    """Retrieve a course's ID based on its name."""
    return service.get_course_id_by_name(course_name)
