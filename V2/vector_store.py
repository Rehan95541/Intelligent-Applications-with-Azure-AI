"""
Vector store — FAISS primary, NumPy fallback.

Same public API regardless of backend.
Supports metadata filtering.
"""

from typing import List, Dict, Any, Optional
import numpy as np


try:
    import faiss
    _HAS_FAISS = True
except ImportError:
    _HAS_FAISS = False


class VectorStore:

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self._vectors = None
        self._metadata = []

        if _HAS_FAISS:
            self._index = faiss.IndexFlatIP(dimension)
            self.backend_name = "FAISS (IndexFlatIP)"
        else:
            self._index = None
            self.backend_name = "NumPy (cosine similarity)"

    def __len__(self):
        return len(self._metadata)

    def add(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]):
        if vectors is None or len(vectors) == 0:
            return

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Expected dimension {self.dimension}, got {vectors.shape[1]}"
            )

        if len(vectors) != len(metadata):
            raise ValueError(
                f"vectors ({len(vectors)}) and metadata ({len(metadata)}) must be same length"
            )

        vectors = vectors.astype(np.float32)

        if _HAS_FAISS:
            self._index.add(vectors)
        else:
            if self._vectors is None:
                self._vectors = vectors
            else:
                self._vectors = np.vstack([self._vectors, vectors])

        self._metadata.extend(metadata)

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 5,
        threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        if len(self) == 0:
            return []

        q = query_vector.astype(np.float32).reshape(1, -1)

        if filters:
            return self._filtered_search(q, k, threshold, filters)

        if _HAS_FAISS:
            sims, indices = self._index.search(q, min(k, len(self)))
            sims = sims[0]
            indices = indices[0]
        else:
            sims_all = (self._vectors @ q.T).flatten()
            top_k = min(k, len(sims_all))
            indices = np.argsort(-sims_all)[:top_k]
            sims = sims_all[indices]

        results = []
        for sim, idx in zip(sims, indices):
            if idx < 0:
                continue
            if float(sim) < threshold:
                continue
            results.append({
                "row_index": int(idx),
                "similarity": round(float(sim), 4),
                "metadata": self._metadata[int(idx)],
            })
        return results

    def _filtered_search(
        self, q: np.ndarray, k: int, threshold: float, filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        allowed = [
            i for i, meta in enumerate(self._metadata)
            if all(str(meta.get(key, "")) == str(val) for key, val in filters.items())
        ]

        if not allowed:
            return []

        if _HAS_FAISS:
            subset = np.zeros((len(allowed), self.dimension), dtype=np.float32)
            for i, idx in enumerate(allowed):
                self._index.reconstruct(int(idx), subset[i])
        else:
            subset = self._vectors[allowed]

        sims = (subset @ q.T).flatten()

        order = np.argsort(-sims)[:k]

        results = []
        for local_idx in order:
            sim = float(sims[local_idx])
            if sim < threshold:
                continue
            global_idx = allowed[int(local_idx)]
            results.append({
                "row_index": int(global_idx),
                "similarity": round(sim, 4),
                "metadata": self._metadata[global_idx],
            })
        return results

    def reset(self):
        self._metadata = []
        self._vectors = None
        if _HAS_FAISS:
            self._index = faiss.IndexFlatIP(self.dimension)