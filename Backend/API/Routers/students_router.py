from fastapi import APIRouter, Query, Path, Depends, HTTPException, status
from typing import Optional, List, Dict
from API.Service.students_service import StudentService
from API.dependencies import get_student_service
from Metrics.metrics import MetricsRoute
from uuid import UUID
from pydantic import BaseModel


class StudentRegistrationStatus(BaseModel):
    registered: bool
    student_id: Optional[UUID] = None


router = APIRouter(prefix="/students", tags=["Students"], route_class=MetricsRoute)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student",
    description=(
        "Registers a new student for a given course using their Discord ID.\n\n"
        "**Returns:** JSON containing the new student's ID and success message."
    ),
)
def register_student(
    name: str = Query(
        ...,
        description="Full name of the student.",
        examples={"example": "Mike Fury Tyson"},
    ),
    discord_id: str = Query(
        ...,
        description="Discord user ID of the student.",
        examples={"example": "discord_12345"},
    ),
    course_id: str = Query(
        ...,
        description="Course ID to register the student in.",
        examples={"example": "uuid-course-123"},
    ),
    service: StudentService = Depends(get_student_service),
) -> Dict[str, str]:
    """Registers a new student for a given course."""
    student = service.create_student(name=name, discord_id=discord_id, course_id=course_id)
    return {"message": "Student registered successfully", "student_id": student["student_id"]}


@router.get(
    "/is_registered",
    response_model=StudentRegistrationStatus,
    summary="Check if a student is registered in a specific course",
    description="Verifies whether a student (via Discord ID) is enrolled in a given course.",
)
def is_registered(
    discord_id: str = Query(
        ...,
        description="Discord ID of the student.",
        examples={"example": "discord_12345"},
    ),
    course_id: str = Query(
        ...,
        description="Course ID to check enrollment for.",
        examples={"example": "uuid-course-123"},
    ),
    service: StudentService = Depends(get_student_service),
) -> Dict[str, Optional[str]]:
    """Checks if a student is already registered in the specified course."""
    students = service.read_all_students(course_id=course_id)
    match = next((s for s in students if s["discord_id"] == discord_id), None)

    if match:
        return {"registered": True, "student_id": match["id"]}
    return {"registered": False}


@router.get(
    "/{discord_id}/courses",
    summary="Get all courses a student (by Discord ID) is registered in",
    description="Returns a list of all courses associated with a specific Discord ID.",
)
def get_registered_courses(
    discord_id: str = Path(
        ...,
        description="Discord ID of the student.",
        examples={"example": "discord_12345"},
    ),
    service: StudentService = Depends(get_student_service),
) -> Dict[str, List[Dict[str, str]]]:
    """Retrieves all courses a student (by Discord ID) is registered in."""
    try:
        courses = service.sql_repo.read_courses_by_discord(discord_id)
        return {"courses": courses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve courses: {e}")


@router.delete(
    "/unregister",
    status_code=status.HTTP_200_OK,
    summary="Unregister a student from a specific course",
    description=(
        "Removes a student's registration from a course using their Discord ID and Course ID.\n\n"
        "**Returns:** JSON message indicating success or failure."
    ),
)
def unregister_student(
    discord_id: str = Query(
        ...,
        description="Discord ID of the student.",
        examples={"example": "discord_12345"},
    ),
    course_id: str = Query(
        ...,
        description="Course ID to remove the student from.",
        examples={"example": "uuid-course-123"},
    ),
    service: StudentService = Depends(get_student_service),
) -> Dict[str, str]:
    """Unregisters a student from a course."""
    try:
        success = service.unregister_student(discord_id=discord_id, course_id=course_id)
        if success:
            return {"message": "Student successfully unregistered from course"}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            error="Student not found or not enrolled in this course",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unregister student: {e}")