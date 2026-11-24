
import yake


class KeywordEngine:

    def __init__(self):

        # English keyword extraction configuration
        self.extractor = yake.KeywordExtractor(
            lan="en",
            n=2,
            dedupLim=0.7,
            top=5,
            features=None
        )

        self.backend_name = "YAKE"

    def extract(self, text):

        if not isinstance(text, str) or not text.strip():
            return []

        # Extract keywords
        keywords = self.extractor.extract_keywords(text)

        # YAKE returns (keyword, score)
        results = []

        for keyword, score in keywords:

            results.append({
                "keyword": keyword,
                "score": round(score, 4)
            })

        return results


# Independent testing
if __name__ == "__main__":

    engine = KeywordEngine()

    feedback = (
        "The battery drains quickly and customer support "
        "did not help me with my problem."
    )

    results = engine.extract(feedback)

    print("Original Feedback:")
    print(feedback)

    print("\nExtracted Keywords:")

    for item in results:

        print(
            item["keyword"],
            "| Score:",
            item["score"]
        )
