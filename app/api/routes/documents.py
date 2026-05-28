from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel
from qdrant_client.http.models import PointStruct

from app.api.deps import EmbeddingsDep, QdrantDep
from app.core.config import settings
from app.core.logger import get_logger
from app.rag.loader import SUPPORTED_EXTENSIONS, load_and_split
from app.rag.vectorstore import ensure_collection

router = APIRouter(prefix="/api/v1", tags=["documents"])
logger = get_logger(__name__)


class UploadResponse(BaseModel):
    filename: str
    chunks: int
    collection: str


@router.post("/upload-doc", response_model=UploadResponse)
async def upload_doc(
    file: UploadFile,
    qdrant: QdrantDep,
    embeddings: EmbeddingsDep,
) -> UploadResponse:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 파일 형식: {ext}")

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        docs = await load_and_split(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    texts = [doc.page_content for doc in docs]
    vectors = await embeddings.aembed_documents(texts)

    await ensure_collection(qdrant, vector_size=len(vectors[0]))

    points = [
        PointStruct(
            id=i,
            vector=vec,
            payload={"text": texts[i], "source": file.filename, **docs[i].metadata},
        )
        for i, vec in enumerate(vectors)
    ]
    await qdrant.upsert(collection_name=settings.qdrant_collection, points=points)

    logger.info("Uploaded %s → %d chunks", file.filename, len(points))
    return UploadResponse(filename=file.filename or "", chunks=len(points), collection=settings.qdrant_collection)
