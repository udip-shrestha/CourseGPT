from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .Routers import queries_router, documents_router, instructors_router, courses_router,students_router
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

# --- THIS MIDDLEWARE CONFIGURATION ---
# Define the origins allowed to make requests (frontend URL)
origins = [
    "http://localhost:5173", # Vite frontend dev server URL
    "http://127.0.0.1:5173",                      # alt local
    "http://sdmay26-37.ece.iastate.edu",          # deployed frontend (HTTP)
    "https://sdmay26-37.ece.iastate.edu",         # deployed frontend (HTTPS - for later)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # List of allowed origins
    allow_credentials=True, # Allow cookies if needed for auth later
    allow_methods=["*"], # Allow all standard methods (GET, POST, PUT, DELETE, OPTIONS,etc.)
    allow_headers=["*"], # Allow all headers
)
# --------------------------------------


app.include_router(queries_router.router)
app.include_router(documents_router.router)
app.include_router(instructors_router.router)
app.include_router(courses_router.router)
app.include_router(students_router.router)


# cd Backend -> make db-init, uvicorn API.main:app --reload
#Find it here: http://127.0.0.1:8000/docs