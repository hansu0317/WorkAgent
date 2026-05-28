from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import EmbeddingsDep, QdrantDep
from app.core.config import settings
from app.core.logger import get_logger

router = APIRouter(prefix="/api/v1", tags=["agent"])
logger = get_logger(__name__)


class AskRequest(BaseModel):
    question: str
    top_k: int = 5


class ChunkResult(BaseModel):
    text: str
    source: str
    score: float


class AskResponse(BaseModel):
    question: str
    results: list[ChunkResult]


@router.post("/ask", response_model=AskResponse)
async def ask(
    body: AskRequest,
    qdrant: QdrantDep,
    embeddings: EmbeddingsDep,
) -> AskResponse:
    vector = await embeddings.aembed_query(body.question)

    hits = await qdrant.search(
        collection_name=settings.qdrant_collection,
        query_vector=vector,
        limit=body.top_k,
        with_payload=True,
    )

    results = [
        ChunkResult(
            text=hit.payload.get("text", "") if hit.payload else "",
            source=hit.payload.get("source", "") if hit.payload else "",
            score=hit.score,
        )
        for hit in hits
    ]

    logger.info("ask: '%s' → %d results", body.question, len(results))
    return AskResponse(question=body.question, results=results)
