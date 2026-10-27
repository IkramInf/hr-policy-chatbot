
from functools import lru_cache
from typing import Any

from qdrant_client import QdrantClient, models
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore

from backend.app.core.config import get_settings
from backend.app.infrastructure.embeddings import get_embedding_model


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    """Create and cache the Qdrant Cloud client."""
    settings = get_settings()

    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key.get_secret_value(),
        timeout=30,
    )


@lru_cache(maxsize=1)
def get_vector_store() -> QdrantVectorStore:
    """Return the (cached) vector store for the configured collection."""
    settings = get_settings()
    client = get_qdrant_client()

    if not client.collection_exists(settings.qdrant_collection):
        raise RuntimeError(
            f"Qdrant collection '{settings.qdrant_collection}' "
            "does not exist. Run the policy ingestion setup first."
        )

    return QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection,
        embedding=get_embedding_model(),
    )


def create_collection(recreate: bool = False) -> None:
    """
    Create the policy collection if it does not exist.

    Set recreate=True only when you intentionally want to delete
    the existing collection and all its stored policy chunks.
    """
    settings = get_settings()
    client = get_qdrant_client()
    collection_name = settings.qdrant_collection

    if client.collection_exists(collection_name):
        if not recreate:
            return

        client.delete_collection(collection_name)

    # all-MiniLM-L6-v2 produces 384-dimensional embeddings.
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=384,
            distance=models.Distance.COSINE,
        ),
    )


def add_policy_chunks(
    documents: list[Document],
    ids: list[str] | None = None,
) -> list[str]:
    """Embed and store policy chunks with their metadata."""
    if not documents:
        return []

    for document in documents:
        if not document.page_content.strip():
            raise ValueError("Policy chunks cannot be empty.")

        required_metadata = ("policy_id", "section_heading")
        missing = [
            key for key in required_metadata
            if not document.metadata.get(key)
        ]
        if missing:
            raise ValueError(
                f"Missing required document metadata: {', '.join(missing)}"
            )

    store = get_vector_store()

    if ids is not None and len(ids) != len(documents):
        raise ValueError("The number of IDs must match the number of chunks.")

    return store.add_documents(documents=documents, ids=ids)


def search_policy(
    question: str,
    top_k: int | None = None,
) -> list[tuple[Document, float]]:
    """Retrieve relevant policy chunks and their similarity scores."""
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    settings = get_settings()
    k = top_k if top_k is not None else settings.retrieval_top_k

    if not 1 <= k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    return get_vector_store().similarity_search_with_score(
        query=question.strip(),
        k=k,
    )


def close_qdrant_client() -> None:
    """Close the Qdrant connection when shutting down the application."""
    if get_qdrant_client.cache_info().currsize:
        get_qdrant_client().close()
        get_qdrant_client.cache_clear()

    get_vector_store.cache_clear()
