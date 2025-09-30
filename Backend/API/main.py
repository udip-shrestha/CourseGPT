from fastapi import FastAPI
from .Routers import questions

app = FastAPI()

app.include_router(questions.router)

# cd Backend -> uvicorn API.main:app --reload
#Find it here: http://127.0.0.1:8000/docs