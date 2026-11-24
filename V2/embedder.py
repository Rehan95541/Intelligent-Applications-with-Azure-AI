"""
Embedder — converts text to vector embeddings.

Uses sentence-transformers/all-MiniLM-L6-v2:
  - 384 dimensions
  - ~90 MB on disk
  - CPU-friendly
  - Good general-purpose English embeddings

Lazy-loads the model so importing this module is cheap.
First call to embed() triggers the model download (one-time).
"""

import threading
from typing import List

import numpy as np


_MODEL_NAME = "all-MiniLM-L6-v2"
_model = None
_model_lock = threading.Lock()


def _load_model():
    """Load the model once, thread-safe."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer(_MODEL_NAME)
    return _model


class Embedder:
    """
    Wraps a SentenceTransformer model.

    Usage:
        emb = Embedder()
        vectors = emb.embed(["battery is bad", "delivery was late"])
        # vectors.shape == (2, 384)

    All vectors are L2-normalized so inner product == cosine similarity.
    """

    def __init__(self, model_name: str = _MODEL_NAME):
        self.model_name = model_name
        self.dimension = 384
        self._local_model = None

    def _get_model(self):
        if self._local_model is None:
            from sentence_transformers import SentenceTransformer
            self._local_model = SentenceTransformer(self.model_name)
        return self._local_model

    def embed(self, texts: List[str], show_progress: bool = False) -> np.ndarray:
        """
        Convert a list of texts to a 2D float32 array of shape (n, 384).
        """
        if not texts:
            return np.zeros((0, self.dimension), dtype=np.float32)

        cleaned = [t if isinstance(t, str) else "" for t in texts]

        model = self._get_model()

        vectors = model.encode(
            cleaned,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=show_progress,
        )

        return vectors.astype(np.float32)

    def embed_one(self, text: str) -> np.ndarray:
        """Embed a single text — returns shape (384,)."""
        return self.embed([text])[0]