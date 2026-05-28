from __future__ import annotations

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

_client: AsyncQdrantClient | None = None


async def get_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        if settings.qdrant_url:
            _client = AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
        else:
            _client = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        logger.info("Qdrant client initialized (collection=%s)", settings.qdrant_collection)
    return _client


async def ensure_collection(client: AsyncQdrantClient, vector_size: int = 1536) -> None:
    exists = await client.collection_exists(settings.qdrant_collection)
    if not exists:
        await client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        logger.info("Created collection: %s", settings.qdrant_collection)
