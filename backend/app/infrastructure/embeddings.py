
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from backend.app.core.config import get_settings


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Initialize and cache the Hugging Face embedding model.

    The same model instance is reused for policy ingestion
    and question retrieval within this process.
    """
    settings = get_settings()

    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def embed_query(text: str) -> list[float]:
    """Convert an employee question into an embedding vector."""
    if not text or not text.strip():
        raise ValueError("Query text cannot be empty.")

    return get_embedding_model().embed_query(text.strip())


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Convert policy text chunks into embedding vectors."""
    if not texts:
        return []

    if any(not text or not text.strip() for text in texts):
        raise ValueError("Document chunks cannot be empty.")

    return get_embedding_model().embed_documents(
        [text.strip() for text in texts]
    )
