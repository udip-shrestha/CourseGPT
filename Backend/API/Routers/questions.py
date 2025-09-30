from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from query import get_answer_from_query
import json
import os
import uuid
from datetime import datetime

router = APIRouter()

QUERIES_FILE = "queries.json"

class QuestionInput(BaseModel):
    question: str
    student_id: str
    course_id: str

def load_queries():
    if os.path.exists(QUERIES_FILE):
        with open(QUERIES_FILE, "r") as f:
            return json.load(f)
    return {"queries": []}

def save_queries(data):
    with open(QUERIES_FILE, "w") as f:
        json.dump(data, f, indent=2)

@router.post("/answer")
async def send_answer(input_data: QuestionInput):
    try:
        # Call AI query function
        result = get_answer_from_query(input_data.question)

        # Load existing queries
        data = load_queries()

        # Generate unique query ID
        query_id = str(uuid.uuid4())

        # Append new query & answer
        data["queries"].append({
            "query_id": query_id,
            "student_id": input_data.student_id,
            "course_id": input_data.course_id,
            "query_text": input_data.question,
            "response_text": result["answer"],
            "asked_at": datetime.now().isoformat()
        })

        # Save back to JSON
        save_queries(data)

        return {"query_id": query_id, "answer": result["answer"], "sources": result.get("sources", [])}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
