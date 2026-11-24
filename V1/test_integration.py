"""
Integration tests for Customer Feedback Intelligence V1.

Covers:
- Valid pipeline run
- Empty feedback
- Missing customer/product values
- Missing required columns (simulated)
- Internal KPI consistency
- Zero-count sentiment categories
- Empty dataset handling
- Complaint category edge cases
"""

import pandas as pd

from sentiment import SentimentEngine
from keywords import KeywordEngine
from complaints import ComplaintEngine
from analytics import BusinessAnalytics
from insights import generate_executive_summary


sentiment_engine = SentimentEngine()
keyword_engine = KeywordEngine()
complaint_engine = ComplaintEngine()
analytics_engine = BusinessAnalytics()


def run_pipeline(df):
    """Replicates app.py pipeline without Flask."""
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()

    required = ["customer_id", "product", "feedback"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    df = df[required]
    df = df.dropna(subset=["feedback"])

    for col in required:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df = df[df["feedback"] != ""]

    if df.empty:
        raise ValueError("No valid feedback records found.")

    sentiment_results = df["feedback"].apply(sentiment_engine.analyze)
    sentiment_df = pd.DataFrame(sentiment_results.tolist())

    df["keywords"] = df["feedback"].apply(keyword_engine.extract)
    df["complaint_categories"] = df["feedback"].apply(complaint_engine.categorize)

    final_df = pd.concat(
        [df.reset_index(drop=True), sentiment_df.reset_index(drop=True)],
        axis=1
    )

    kpis = analytics_engine.calculate(final_df)

    complaint_counts = {
        item["category"]: item["count"]
        for item in kpis["complaint_summary"]
    }

    product_summary_for_report = [
        {
            "product": item["product"],
            "feedback_count": item["total_feedback"],
            "positive_rate": item["positive_rate"],
            "negative_rate": item["negative_rate"]
        }
        for item in kpis["product_summary"]
    ]

    top_keyword_names = [item["keyword"] for item in kpis["top_keywords"]]

    report_data = {
        "total_feedback": kpis["total_feedback"],
        "sentiment_counts": kpis["sentiment_counts"],
        "sentiment_percentages": kpis["sentiment_percentages"],
        "product_summary": product_summary_for_report,
        "complaint_counts": complaint_counts,
        "top_keywords": top_keyword_names
    }

    report = generate_executive_summary(report_data)
    return final_df, kpis, report


def assert_true(condition, label):
    if condition:
        print(f"  PASS: {label}")
    else:
        print(f"  FAIL: {label}")
        raise AssertionError(label)


# ============================================
# TEST 1: Valid dataset
# ============================================
print("\n=== TEST 1: Valid dataset ===")

valid_df = pd.DataFrame({
    "customer_id": ["C001", "C002", "C003", "C004", "C005"],
    "product": ["Laptop", "Laptop", "Phone", "Phone", "Tablet"],
    "feedback": [
        "Excellent battery life and fast performance",
        "The battery drains quickly and support was unhelpful",
        "Amazing camera, very happy",
        "Delivery was late and product arrived damaged",
        "Okay product for the price"
    ]
})

final_df, kpis, report = run_pipeline(valid_df)

assert_true(kpis["total_feedback"] == 5, "Total feedback = 5")
assert_true(kpis["unique_customers"] == 5, "Unique customers = 5")
assert_true(
    sum(kpis["sentiment_counts"].values()) == 5,
    "Sentiment counts sum to total"
)
assert_true(
    abs(sum(kpis["sentiment_percentages"].values()) - 100.0) < 0.1,
    "Sentiment percentages sum to ~100"
)
assert_true(
    kpis["sentiment_balance"] ==
    round(kpis["positive_rate"] - kpis["negative_rate"], 2),
    "Sentiment balance = positive - negative"
)
assert_true(report["status"] == "Generated", "Report status = Generated")
assert_true(report["method"] == "Template-based", "Report method = Template-based")
assert_true(len(report["recommendations"]) > 0, "At least one recommendation")


# ============================================
# TEST 2: Missing customer/product values
# ============================================
print("\n=== TEST 2: Missing customer/product values ===")

missing_df = pd.DataFrame({
    "customer_id": ["C001", None, "C003"],
    "product": [None, "Phone", "Laptop"],
    "feedback": ["Good product", "Bad battery", "Slow performance"]
})

final_df, kpis, report = run_pipeline(missing_df)

assert_true(kpis["total_feedback"] == 3, "Total feedback = 3")
assert_true(kpis["unique_customers"] == 2, "Unique customers = 2 (blank excluded)")
assert_true(report["status"] == "Generated", "Report still generated")


# ============================================
# TEST 3: Empty feedback rows dropped
# ============================================
print("\n=== TEST 3: Empty feedback rows dropped ===")

empty_feedback_df = pd.DataFrame({
    "customer_id": ["C001", "C002", "C003"],
    "product": ["Laptop", "Phone", "Tablet"],
    "feedback": ["Good product", "   ", ""]
})

final_df, kpis, report = run_pipeline(empty_feedback_df)

assert_true(kpis["total_feedback"] == 1, "Only 1 valid feedback remains")


# ============================================
# TEST 4: All feedback empty -> raises
# ============================================
print("\n=== TEST 4: All feedback empty raises ===")

all_empty_df = pd.DataFrame({
    "customer_id": ["C001"],
    "product": ["Laptop"],
    "feedback": ["   "]
})

try:
    run_pipeline(all_empty_df)
    assert_true(False, "Should have raised ValueError")
except ValueError as e:
    assert_true("No valid feedback" in str(e), "Correct error raised")


# ============================================
# TEST 5: Missing required column raises
# ============================================
print("\n=== TEST 5: Missing required column raises ===")

bad_cols_df = pd.DataFrame({
    "customer_id": ["C001"],
    "feedback": ["Good"]
})

try:
    run_pipeline(bad_cols_df)
    assert_true(False, "Should have raised ValueError")
except ValueError as e:
    assert_true("Missing column" in str(e), "Correct error raised")


# ============================================
# TEST 6: Zero-count sentiment category
# ============================================
print("\n=== TEST 6: Zero-count sentiment category ===")

all_positive_df = pd.DataFrame({
    "customer_id": ["C001", "C002"],
    "product": ["Laptop", "Laptop"],
    "feedback": ["Excellent product", "Amazing quality and fast delivery"]
})

final_df, kpis, report = run_pipeline(all_positive_df)

assert_true("Negative" in kpis["sentiment_counts"], "Negative key exists")
assert_true(kpis["sentiment_counts"]["Negative"] == 0, "Negative count = 0")
assert_true(kpis["sentiment_percentages"]["Negative"] == 0.0, "Negative % = 0")
assert_true(report["status"] == "Generated", "Report generated with zero negative")


# ============================================
# TEST 7: Insights empty dataset
# ============================================
print("\n=== TEST 7: Insights empty dataset ===")

empty_report = generate_executive_summary({
    "total_feedback": 0,
    "sentiment_counts": {},
    "sentiment_percentages": {},
    "product_summary": [],
    "complaint_counts": {},
    "top_keywords": []
})

assert_true(empty_report["status"] == "No data", "Status = No data")
assert_true(len(empty_report["recommendations"]) > 0, "Fallback recommendation present")


# ============================================
# TEST 8: Complaint categories are multi-label
# ============================================
print("\n=== TEST 8: Multi-label complaint detection ===")

multi_df = pd.DataFrame({
    "customer_id": ["C001"],
    "product": ["Laptop"],
    "feedback": ["Battery drains fast and delivery was late and support was slow"]
})

final_df, kpis, report = run_pipeline(multi_df)

cats = final_df.iloc[0]["complaint_categories"]
assert_true(len(cats) >= 2, f"Multiple categories detected: {cats}")


# ============================================
# TEST 9: Percentage consistency in product summary
# ============================================
print("\n=== TEST 9: Product summary consistency ===")

for product in kpis["product_summary"]:
    pos_pct = (product["positive"] / product["total_feedback"]) * 100
    neg_pct = (product["negative"] / product["total_feedback"]) * 100
    assert_true(
        abs(product["positive_rate"] - round(pos_pct, 2)) < 0.01,
        f"{product['product']} positive_rate consistent"
    )
    assert_true(
        abs(product["negative_rate"] - round(neg_pct, 2)) < 0.01,
        f"{product['product']} negative_rate consistent"
    )


# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 50)
print("ALL INTEGRATION TESTS PASSED")
print("=" * 50)