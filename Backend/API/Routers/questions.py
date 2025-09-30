from fastapi import APIRouter

router = APIRouter()

@router.get("/query")
async def get_query():
    return {"message": "No query yet"}

@router.post("/answer")
async def send_answer():
    return {"message": "No answer yet"}
