"""
RAG engine — ties together filters, embeddings, vector search, and answer generation.
"""

import numpy as np

from embedder import Embedder
from vector_store import VectorStore
from llm_backend import get_llm_backend


class RagEngine:

    def __init__(self):
        self.embedder = Embedder()
        self.store = VectorStore(dimension=self.embedder.dimension)
        self.llm = get_llm_backend()
        self._row_count = 0

    def index(self, df):
        """Build the vector index from the uploaded DataFrame."""
        self.store.reset()

        if df is None or df.empty:
            self._row_count = 0
            return

        texts = df["feedback"].astype(str).tolist()
        vectors = self.embedder.embed(texts, show_progress=False)

        metadata = []
        for i, row in enumerate(df.itertuples(index=False)):
            metadata.append({
                "row_index": i,
                "customer_id": str(getattr(row, "customer_id", "")),
                "product": str(getattr(row, "product", "")),
                "feedback": str(getattr(row, "feedback", "")),
                "sentiment": str(getattr(row, "sentiment", "")),
                "sentiment_score": float(getattr(row, "sentiment_score", 0.0)),
                "complaint_categories": list(getattr(row, "complaint_categories", [])),
                "keywords": list(getattr(row, "keywords", [])),
            })

        self.store.add(vectors, metadata)
        self._row_count = len(df)

    def ask(self, question, filters=None, top_k=5, threshold=0.15):
        """Ask a question about the indexed feedback."""
        if not question or not question.strip():
            return {
                "answer": "Please enter a question.",
                "sources": [],
                "backend": self.llm.name,
                "filters": filters or {},
                "threshold": threshold,
                "total_indexed": self._row_count,
            }

        if self._row_count == 0:
            return {
                "answer": "No feedback has been indexed yet. Upload a CSV first.",
                "sources": [],
                "backend": self.llm.name,
                "filters": filters or {},
                "threshold": threshold,
                "total_indexed": 0,
            }

        filters = {k: v for k, v in (filters or {}).items() if v}

        question_vector = self.embedder.embed_one(question)

        results = self.store.search(
            question_vector,
            k=top_k,
            threshold=threshold,
            filters=filters if filters else None,
        )

        if not results and filters:
            unfiltered = self.store.search(
                question_vector, k=top_k, threshold=threshold, filters=None
            )
            if unfiltered:
                return {
                    "answer": (
                        f"No reviews match the current filters {filters}. "
                        f"However, {len(unfiltered)} reviews match the question "
                        f"without filters. Try clearing one or more filters."
                    ),
                    "sources": [
                        {
                            "feedback": r["metadata"].get("feedback", ""),
                            "product": r["metadata"].get("product", ""),
                            "sentiment": r["metadata"].get("sentiment", ""),
                            "similarity": r["similarity"],
                        }
                        for r in unfiltered
                    ],
                    "backend": self.llm.name,
                    "filters": filters,
                    "threshold": threshold,
                    "total_indexed": self._row_count,
                }

        answer = self.llm.generate(question, results, filters)

        sources = [
            {
                "feedback": r["metadata"].get("feedback", ""),
                "product": r["metadata"].get("product", ""),
                "sentiment": r["metadata"].get("sentiment", ""),
                "similarity": r["similarity"],
            }
            for r in results
        ]

        return {
            "answer": answer,
            "sources": sources,
            "backend": self.llm.name,
            "filters": filters,
            "threshold": threshold,
            "total_indexed": self._row_count,
        }

    def available_filters(self):
        products = set()
        sentiments = set()
        categories = set()
        for meta in self.store._metadata:
            if meta.get("product"):
                products.add(meta["product"])
            if meta.get("sentiment"):
                sentiments.add(meta["sentiment"])
            for c in meta.get("complaint_categories", []):
                if c and c != "Other":
                    categories.add(c)
        return {
            "products": sorted(products),
            "sentiments": sorted(sentiments),
            "categories": sorted(categories),
        }