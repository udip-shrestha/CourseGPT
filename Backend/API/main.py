from contextlib import asynccontextmanager
from fastapi import FastAPI
from .Routers import questions, document_router, instructors_router, courses_router
from API.dependencies import get_connection_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context: initialize and clean up shared resources."""
    # ---- STARTUP ----
    connection_manager = get_connection_manager()

    yield

    # ---- SHUTDOWN ----
    connection_manager.close_all()

app = FastAPI(lifespan=lifespan)

app.include_router(questions.router)
app.include_router(document_router.router)
app.include_router(instructors_router.router)
app.include_router(courses_router.router)


# cd Backend -> make db-init, uvicorn API.main:app --reload
#Find it here: http://127.0.0.1:8000/docs