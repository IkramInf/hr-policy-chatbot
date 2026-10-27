
import logging
from functools import lru_cache
from pathlib import Path

from fastembed import TextEmbedding
from langchain_core.embeddings import Embeddings

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)

# Stored inside the project so a model downloaded at build time is still
# there at runtime (the default temp folder is not kept on most hosts).
MODEL_CACHE_DIR = Path(__file__).resolve().parents[3] / ".cache" / "fastembed"


class FastEmbedEmbeddings(Embeddings):
    """
    Same all-MiniLM-L6-v2 model as before, run with ONNX instead of PyTorch.

    It needs roughly 200 MB of RAM instead of 1 GB+, so it fits on small
    hosts such as Render's free tier.
    """

    def __init__(self, model_name: str) -> None:
        self._model = TextEmbedding(
            model_name=model_name,
            cache_dir=str(MODEL_CACHE_DIR),
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


@lru_cache(maxsize=1)
def get_embedding_model() -> FastEmbedEmbeddings:
    """Load and cache the embedding model (once per process)."""
    settings = get_settings()
    logger.info("Loading embedding model %s ...", settings.embedding_model)

    model = FastEmbedEmbeddings(settings.embedding_model)

    logger.info("Embedding model ready.")
    return model


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
