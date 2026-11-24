
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentEngine:

    def __init__(self):

        self.analyzer = SentimentIntensityAnalyzer()
        self.backend_name = "VADER"

    def analyze(self, text):

        scores = self.analyzer.polarity_scores(text)

        compound = scores["compound"]

        if compound >= 0.05:
            sentiment = "Positive"

        elif compound <= -0.05:
            sentiment = "Negative"

        else:
            sentiment = "Neutral"

        return {

            "sentiment": sentiment,

            "positive_score": scores["pos"],

            "negative_score": scores["neg"],

            "neutral_score": scores["neu"],

            "compound_score": compound,

            # Standardized score for all future backends
            "sentiment_score": compound,

            "backend": self.backend_name

        }


if __name__ == "__main__":

    engine = SentimentEngine()

    examples = [
        "Excellent product and amazing performance.",
        "The product is terrible.",
        "The product is okay."
    ]

    for feedback in examples:

        print("\nFeedback:", feedback)

        print(engine.analyze(feedback))
