from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Literal, Optional
from uuid import UUID
import psycopg2
import os

router = APIRouter()

QUERIES_FILE = "Discord/students.json"

class CourseInput(BaseModel):
    name: str
    institution: str
    semester: Literal["FALL", "SPRING", "SUMMER"]
    year: int
    instructor_id: Optional[UUID] = None
    course_description: Optional[str] = None
    credit_points: Optional[int] = None


# --- Database connection ---
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "course_gpt"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "yourpassword"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )

@router.get("/instructors/{instructor_id}/courses")
async def get_courses(instructor_id: int):
    """
    Retrieve a list of all courses by instructor Id.
    """
    try:

        return {"message": "List of items"}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

# --- Create course endpoint ---
@router.post("/courses")
def create_course(course: CourseInput):
    """
    Create a new course and link it via instructor Id.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Find semester ID
        cur.execute("SELECT id FROM semesters WHERE name = %s", (course.semester.upper(),))
        semester_row = cur.fetchone()
        if not semester_row:
            raise HTTPException(status_code=400, detail="Invalid semester name.")
        semester_id = semester_row[0]

        # Insert course into DB
        cur.execute("""
            INSERT INTO courses (name, institution, semester_id, year, instructor_id, course_description, credit_points)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            course.name,
            course.institution,
            semester_id,
            course.year,
            course.instructor_id,
            course.course_description,
            course.credit_points
        ))

        course_id = cur.fetchone()[0]
        conn.commit()
        return {"message": "Course created successfully", "course_id": course_id}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cur.close()
        conn.close()