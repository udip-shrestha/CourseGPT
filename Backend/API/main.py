import logging
import time
from contextlib import asynccontextmanager
from math import exp
from fastapi.routing import APIRoute
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from .Routers import queries_router, documents_router, instructors_router, courses_router,students_router, auth_router, web_socket_router
from API.dependencies import get_connection_manager
from prometheus_client import CollectorRegistry, multiprocess, generate_latest, CONTENT_TYPE_LATEST
from Metrics.metrics import MetricsRoute, metrics_response

logging.basicConfig(
    level=logging.INFO,     # Enables INFO logs (fixes your issue)
    format="[%(levelname)s] %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context: initialize and clean up shared resources."""
    # ---- STARTUP ----
    connection_manager = get_connection_manager()

    yield

    # ---- SHUTDOWN ----
    connection_manager.close_all()


app = FastAPI(lifespan=lifespan)

# Apply MetricsRoute to all routers
app.router.route_class = MetricsRoute
queries_router.router.route_class = MetricsRoute
documents_router.router.route_class = MetricsRoute
instructors_router.router.route_class = MetricsRoute
courses_router.router.route_class = MetricsRoute
students_router.router.route_class = MetricsRoute
auth_router.router.route_class = MetricsRoute
web_socket_router.router.route_class = MetricsRoute

# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


app.include_router(queries_router.router)
app.include_router(documents_router.router)
app.include_router(instructors_router.router)
app.include_router(courses_router.router)
app.include_router(students_router.router)
app.include_router(auth_router.router)
app.include_router(web_socket_router.router)


# --- THIS MIDDLEWARE CONFIGURATION ---
# Define the origins allowed to make requests (frontend URL)
origins = [
    "http://localhost:5173", # Vite frontend dev server URL
    "http://127.0.0.1:5173",                      # alt local
    "http://sdmay26-37.ece.iastate.edu",          # deployed frontend (HTTP)
    "https://sdmay26-37.ece.iastate.edu",         # deployed frontend (HTTPS - for later)
]

app = CORSMiddleware(
    app=app,
    allow_origins=origins, # List of allowed origins
    allow_credentials=True, # Allow cookies if needed for auth later
    allow_methods=["*"], # Allow all standard methods (GET, POST, PUT, DELETE, OPTIONS,etc.)
    allow_headers=["*"], # Allow all headers
    expose_headers=["Content-Disposition"]
)
# --------------------------------------


# cd Backend -> make db-init, uvicorn API.main:app --reload
#Find it here: http://127.0.0.1:8000/docs