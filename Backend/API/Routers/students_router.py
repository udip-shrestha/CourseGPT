from fastapi import APIRouter, Query, Path, Depends, HTTPException, status
from typing import Optional, List, Dict
from API.Service.students_service import StudentService
from API.dependencies import get_student_service
from uuid import UUID
from pydantic import BaseModel

class StudentRegistrationStatus(BaseModel):
    registered: bool
    student_id: Optional[UUID] = None

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)

# ------------------------------------------------------
# Register Student
# ------------------------------------------------------
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
    name: str = Query(..., description="Full name of the student.", example="Mike Fury Tyson"),
    discord_id: str = Query(..., description="Discord user ID of the student.", example="discord_12345"),
    course_id: str = Query(..., description="Course ID to register the student in.", example="uuid-course-123"),
    service: StudentService = Depends(get_student_service)
) -> Dict[str, str]:
    student = service.create_student(name=name, discord_id=discord_id, course_id=course_id)
    return {"message": "Student registered successfully", "student_id": student["student_id"]}


# ------------------------------------------------------
# Check if a Student is Registered in a Course
# ------------------------------------------------------
@router.get(
    "/is_registered", 
    response_model=StudentRegistrationStatus,
    summary="Check if a student is registered in a specific course",
    description="Verifies whether a student (via Discord ID) is enrolled in a given course."
)
def is_registered(
    discord_id: str = Query(..., description="Discord ID of the student."),
    course_id: str = Query(..., description="Course ID to check enrollment for."),
    service: StudentService = Depends(get_student_service)
) -> Dict[str, Optional[str]]:
    students = service.read_all_students(course_id=course_id)
    match = next((s for s in students if s["discord_id"] == discord_id), None)

    if match:
        return {"registered": True, "student_id": match["id"]}
    return {"registered": False}

# ------------------------------------------------------
# Get Courses Registered by Discord ID
# ------------------------------------------------------
@router.get(
    "/{discord_id}/courses",
    summary="Get all courses a student (by Discord ID) is registered in",
    description="Returns a list of all courses associated with a specific Discord ID."
)
def get_registered_courses(
    discord_id: str = Path(..., description="Discord ID of the student."),
    service: StudentService = Depends(get_student_service)
) -> Dict[str, List[Dict[str, str]]]:
    try:
        courses = service.sql_repo.read_courses_by_discord(discord_id)
        return {"courses": courses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve courses: {e}")
