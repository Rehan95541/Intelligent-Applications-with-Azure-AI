
from collections import Counter
import pandas as pd


class BusinessAnalytics:

    def calculate(self, df):

        if df.empty:
            raise ValueError("No feedback records available.")

        total = len(df)

        # --------------------------------
        # 1. Customer KPIs
        # --------------------------------

        unique_customers = (
            df["customer_id"]
            .replace("", pd.NA)
            .nunique()
        )

        # --------------------------------
        # 2. Sentiment distribution
        # --------------------------------

        sentiment_types = [
            "Positive",
            "Neutral",
            "Negative"
        ]

        sentiment_counts = (
            df["sentiment"]
            .value_counts()
            .to_dict()
        )

        # Include zero-count categories
        for sentiment in sentiment_types:

            sentiment_counts.setdefault(sentiment, 0)

        sentiment_percentages = {}

        for sentiment in sentiment_types:

            percentage = (
                sentiment_counts[sentiment] / total
            ) * 100

            sentiment_percentages[sentiment] = round(
                percentage, 2
            )

        # --------------------------------
        # 3. Sentiment KPIs
        # --------------------------------

        positive_rate = sentiment_percentages["Positive"]
        negative_rate = sentiment_percentages["Negative"]
        neutral_rate = sentiment_percentages["Neutral"]

        sentiment_balance = positive_rate - negative_rate

        average_sentiment_score = round(
            df["sentiment_score"].mean(), 4
        )

        # --------------------------------
        # 4. Product-wise analytics
        # --------------------------------

        product_summary = []

        for product, group in df.groupby(
            "product",
            sort=True
        ):

            product_total = len(group)

            positive = int(
                (group["sentiment"] == "Positive").sum()
            )

            negative = int(
                (group["sentiment"] == "Negative").sum()
            )

            neutral = int(
                (group["sentiment"] == "Neutral").sum()
            )

            product_positive_rate = (
                positive / product_total
            ) * 100

            product_negative_rate = (
                negative / product_total
            ) * 100

            product_summary.append({

                "product": product,

                "total_feedback": product_total,

                "positive": positive,

                "neutral": neutral,

                "negative": negative,

                "positive_rate": round(
                    product_positive_rate, 2
                ),

                "negative_rate": round(
                    product_negative_rate, 2
                ),

                "average_sentiment_score": round(
                    group["sentiment_score"].mean(), 4
                )

            })

        # --------------------------------
        # 5. Complaint analytics
        # --------------------------------

        complaint_counter = Counter()

        for categories in df["complaint_categories"]:

            # One count per category per record
            unique_categories = set(categories)

            for category in unique_categories:

                if category != "Other":

                    complaint_counter[category] += 1

        complaint_summary = []

        for category, count in complaint_counter.most_common():

            complaint_summary.append({

                "category": category,

                "count": count,

                "percentage": round(
                    (count / total) * 100, 2
                )

            })

        # --------------------------------
        # 6. Keyword analytics
        # --------------------------------

        keyword_counter = Counter()

        for keyword_list in df["keywords"]:

            # Avoid duplicate keywords in one record
            unique_keywords = {
                item["keyword"].strip().casefold()
                for item in keyword_list
                if item.get("keyword", "").strip()
            }

            keyword_counter.update(unique_keywords)

        top_keywords = [

            {
                "keyword": keyword,
                "count": count
            }

            for keyword, count in keyword_counter.most_common(10)

        ]

        # --------------------------------
        # 7. Final KPI response
        # --------------------------------

        return {

            "total_feedback": total,

            "unique_customers": int(unique_customers),

            "sentiment_counts": sentiment_counts,

            "sentiment_percentages": sentiment_percentages,

            "positive_rate": positive_rate,

            "negative_rate": negative_rate,

            "neutral_rate": neutral_rate,

            "sentiment_balance": round(
                sentiment_balance, 2
            ),

            "average_sentiment_score": average_sentiment_score,

            "product_summary": product_summary,

            "complaint_summary": complaint_summary,

            "top_keywords": top_keywords

        }
