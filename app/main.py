from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import agent, documents
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Personal Work Agent (env=%s)", settings.app_env)
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Personal Work Agent",
    description="회사 업무 자동화 AI 비서",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(documents.router)
app.include_router(agent.router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}
