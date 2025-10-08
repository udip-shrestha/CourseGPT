from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Literal

router = APIRouter()

QUERIES_FILE = "Discord/students.json"

class CourseInput(BaseModel):
    course_name: str
    semester: Literal["Fall", "Spring", "Summer"]
    documents: list[str]
    instructor_id: int
    course_description: str
    credit_points : int
    year: int

@router.get("/instructors/{instructor_id}/courses")
async def get_courses(instructor_id: int):
    """
    Retrieve a list of all courses by instructor Id.
    """
    try:

        return {"message": "List of items"}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.post("/courses/")
async def create_course(course: CourseInput):
    """
    Create a new course and link it via instructor Id.
    """
    try:

        return {"message": "List of items"}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
