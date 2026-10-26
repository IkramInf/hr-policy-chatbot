
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import chat, health, policies
from backend.app.core.config import get_settings
from backend.app.infrastructure.vector_store import close_qdrant_client

settings = get_settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    logger.info("Starting %s", settings.app_name)

    yield

    close_qdrant_client()
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="An HR policy assistant grounded in indexed policy documents.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(
    health.router,
    prefix=settings.api_prefix,
)
app.include_router(
    chat.router,
    prefix=settings.api_prefix,
)
app.include_router(
    policies.router,
    prefix=settings.api_prefix,
)


@app.get("/")
def root() -> dict[str, str]:
    """Provide a basic API welcome response."""
    return {
        "service": settings.app_name,
        "status": "running",
        "docs": "/docs",
    }
