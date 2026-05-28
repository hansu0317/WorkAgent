from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from langchain_openai import OpenAIEmbeddings
from qdrant_client import AsyncQdrantClient

from app.rag.embeddings import get_embeddings
from app.rag.vectorstore import get_client

QdrantDep = Annotated[AsyncQdrantClient, Depends(get_client)]
EmbeddingsDep = Annotated[OpenAIEmbeddings, Depends(get_embeddings)]
