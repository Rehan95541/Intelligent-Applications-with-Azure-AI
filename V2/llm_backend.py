"""
LLM backend interface.

V2 default: TemplateBackend (no LLM, structured answer from retrieved rows).
V2 future: CloudLLMBackend can drop in via LLM_PROVIDER env var.
"""

import os
from collections import Counter


class TemplateBackend:
    """
    Builds an answer from retrieved rows without any LLM.
    """

    name = "Template-based (no LLM)"

    def generate(self, question, sources, filters=None):
        if not sources:
            return (
                "No relevant reviews were found for this question with the "
                "current filters. Try lowering the similarity threshold, "
                "clearing filters, or rephrasing the question."
            )

        filters = filters or {}
        filter_text = self._format_filters(filters)

        lines = []
        lines.append(
            f"Found {len(sources)} relevant review(s){filter_text}."
        )

        sentiments = [s["metadata"].get("sentiment", "Unknown") for s in sources]
        pos = sentiments.count("Positive")
        neg = sentiments.count("Negative")
        neu = sentiments.count("Neutral")

        if len(sources) >= 2:
            lines.append(
                f"Sentiment in these reviews: {pos} positive, "
                f"{neu} neutral, {neg} negative."
            )

        categories = []
        for s in sources:
            for c in s["metadata"].get("complaint_categories", []):
                if c and c != "Other":
                    categories.append(c)

        if categories:
            top_cats = Counter(categories).most_common(3)
            cat_text = ", ".join(f"{c} ({n})" for c, n in top_cats)
            lines.append(f"Recurring complaint themes: {cat_text}.")

        keywords = []
        for s in sources:
            for kw in s["metadata"].get("keywords", []):
                if isinstance(kw, dict):
                    k = kw.get("keyword", "").strip()
                else:
                    k = str(kw).strip()
                if k:
                    keywords.append(k.lower())

        if keywords:
            top_kw = Counter(keywords).most_common(5)
            kw_text = ", ".join(f"{k}" for k, _ in top_kw)
            lines.append(f"Common keywords in these reviews: {kw_text}.")

        lines.append("Representative feedback:")
        for src in sources[:2]:
            feedback = src["metadata"].get("feedback", "").strip()
            product = src["metadata"].get("product", "Unknown")
            sim = src["similarity"]
            lines.append(
                f'  - "{feedback}" (product: {product}, similarity: {sim:.2f})'
            )

        lines.append(
            "Note: This answer is a structured summary of the retrieved reviews. "
            "It does not infer causes or add information outside the dataset."
        )

        return "\n".join(lines)

    def _format_filters(self, filters):
        if not filters:
            return ""
        parts = [f"{k}={v}" for k, v in filters.items()]
        return " (filters: " + ", ".join(parts) + ")"


class CloudLLMBackend:
    """
    Placeholder for future cloud LLM. Not active in V2.
    """

    name = "Cloud LLM (not configured)"

    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.endpoint = os.getenv("LLM_ENDPOINT", "")
        self.model = os.getenv("LLM_MODEL", "")

    def generate(self, question, sources, filters=None):
        if not self.api_key:
            raise RuntimeError(
                "LLM_PROVIDER=cloud but LLM_API_KEY is not set in .env"
            )
        raise NotImplementedError(
            "Cloud LLM backend will be implemented in a later patch."
        )


def get_llm_backend():
    provider = os.getenv("LLM_PROVIDER", "template").lower()
    if provider == "cloud":
        return CloudLLMBackend()
    return TemplateBackend()