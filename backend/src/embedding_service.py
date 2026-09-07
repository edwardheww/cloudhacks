"""BGE-M3 embedding utilities used by indexing and semantic search."""

from __future__ import annotations

from collections.abc import Iterable

MODEL_NAME = "BAAI/bge-m3"
EMBEDDING_DIMENSIONS = 1024


def deal_to_embedding_text(deal: dict) -> str:
    """Build one searchable description from a structured deal."""
    fields = (
        deal.get("restaurant"),
        deal.get("title"),
        deal.get("cuisine"),
        deal.get("location"),
        deal.get("discount"),
        deal.get("price"),
        deal.get("raw_text"),
    )
    return ". ".join(str(value).strip() for value in fields if value)


def vector_to_pgvector(vector: Iterable[float]) -> str:
    """Format a vector for PostgreSQL's pgvector input syntax."""
    return "[" + ",".join(str(float(value)) for value in vector) + "]"


class EmbeddingService:
    """Lazy BGE-M3 model wrapper.

    The model is intentionally loaded only when embeddings are requested: this
    keeps ordinary database scripts usable before the model dependencies exist.
    """

    def __init__(self, model_name: str = MODEL_NAME, use_fp16: bool = False):
        self.model_name = model_name
        self.use_fp16 = use_fp16
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from FlagEmbedding import BGEM3FlagModel
            except ImportError as error:
                raise RuntimeError(
                    "Missing AI dependencies. Activate backend/.venv and run "
                    "`pip install -r requirements.txt`."
                ) from error

            self._model = BGEM3FlagModel(self.model_name, use_fp16=self.use_fp16)
        return self._model

    def embed(self, texts: list[str], batch_size: int = 4) -> list[list[float]]:
        if not texts:
            return []

        result = self._get_model().encode(
            texts,
            batch_size=batch_size,
            max_length=8192,
        )
        vectors = result["dense_vecs"]

        if len(vectors[0]) != EMBEDDING_DIMENSIONS:
            raise ValueError(
                f"Expected {EMBEDDING_DIMENSIONS}-dimension BGE-M3 vectors, "
                f"received {len(vectors[0])}."
            )

        return [list(map(float, vector)) for vector in vectors]
