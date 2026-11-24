
import pandas as pd

from analytics import BusinessAnalytics


# Create a small test dataset
data = {

    "customer_id": [
        "C001", "C002", "C003", "C004"
    ],

    "product": [
        "Laptop", "Laptop", "Phone", "Phone"
    ],

    "feedback": [
        "Excellent battery",
        "Very slow performance",
        "Amazing camera",
        "Poor battery"
    ],

    "sentiment": [
        "Positive",
        "Negative",
        "Positive",
        "Negative"
    ],

    "sentiment_score": [
        0.8, -0.7, 0.9, -0.8
    ],

    "complaint_categories": [
        ["Battery"],
        ["Performance"],
        ["Other"],
        ["Battery"]
    ],

    "keywords": [
        [{"keyword": "battery"}],
        [{"keyword": "performance"}],
        [{"keyword": "camera"}],
        [{"keyword": "battery"}]
    ]

}


df = pd.DataFrame(data)

engine = BusinessAnalytics()

results = engine.calculate(df)


print("\n========== BUSINESS KPI TEST ==========")

print("Total Feedback:", results["total_feedback"])

print("Unique Customers:", results["unique_customers"])

print("Positive Rate:", results["positive_rate"], "%")

print("Negative Rate:", results["negative_rate"], "%")

print("Neutral Rate:", results["neutral_rate"], "%")

print("Sentiment Balance:", results["sentiment_balance"])

print(
    "Average Sentiment Score:",
    results["average_sentiment_score"]
)


print("\n========== PRODUCT SUMMARY ==========")

for product in results["product_summary"]:
    print(product)


print("\n========== COMPLAINT SUMMARY ==========")

for complaint in results["complaint_summary"]:
    print(complaint)


print("\n========== TOP KEYWORDS ==========")

for keyword in results["top_keywords"]:
    print(keyword)


print("\nAnalytics test completed!")
