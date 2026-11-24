
import re


class ComplaintEngine:

    def __init__(self):

        self.categories = {

            "Battery": [
                "battery",
                "charging",
                "charge",
                "drains",
                "discharge"
            ],

            "Delivery": [
                "delivery",
                "shipping",
                "shipment",
                "late",
                "arrived"
            ],

            "Product Quality": [
                "damaged",
                "broken",
                "defective",
                "quality",
                "stopped working"
            ],

            "Performance": [
                "slow",
                "hanging",
                "freezing",
                "lag",
                "performance"
            ],

            "Customer Support": [
                "support",
                "customer service",
                "assistance",
                "help",
                "complaint"
            ],

            "Price": [
                "expensive",
                "costly",
                "price",
                "overpriced",
                "affordable"
            ]

        }

        self.backend_name = "Rule-Based"

    def categorize(self, text):

        if not isinstance(text, str) or not text.strip():
            return ["Other"]

        text = text.lower()

        # Normalize punctuation for matching
        normalized = re.sub(r"[^a-z0-9\s]", " ", text)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        detected_categories = []

        for category, keywords in self.categories.items():

            for keyword in keywords:

                pattern = (
                    r"(?<![a-z0-9])"
                    + re.escape(keyword)
                    + r"(?![a-z0-9])"
                )

                if re.search(pattern, normalized):

                    detected_categories.append(category)

                    # Avoid adding same category multiple times
                    break

        if not detected_categories:
            return ["Other"]

        return detected_categories


# Independent testing
if __name__ == "__main__":

    engine = ComplaintEngine()

    examples = [
        "The battery drains quickly.",
        "The delivery was late and product arrived damaged.",
        "Customer support did not help me.",
        "The laptop is very slow and expensive."
    ]

    for feedback in examples:

        print("\nFeedback:", feedback)

        print(
            "Categories:",
            engine.categorize(feedback)
        )
