
# insights.py

"""
Executive Summary and Business Insights Generator

V1 implementation:
- Template-based report generation
- No external API required
- Uses calculated business metrics
- Produces evidence-based recommendations
"""


def safe_percentage(value):
    """Convert a numeric percentage into a readable string."""
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "N/A"


def generate_executive_summary(report_data):
    """
    Generate an executive summary from standardized analytics data.

    Expected input:
    {
        "total_feedback": 100,
        "sentiment_counts": {
            "Positive": 55,
            "Neutral": 25,
            "Negative": 20
        },
        "sentiment_percentages": {
            "Positive": 55,
            "Neutral": 25,
            "Negative": 20
        },
        "product_summary": [
            {
                "product": "Laptop",
                "feedback_count": 40,
                "positive_rate": 60,
                "negative_rate": 25
            }
        ],
        "complaint_counts": {
            "Battery": 15,
            "Delivery": 8
        },
        "top_keywords": ["battery", "quality", "delivery"]
    }
    """

    total = int(report_data.get("total_feedback", 0) or 0)

    counts = report_data.get("sentiment_counts", {})
    percentages = report_data.get("sentiment_percentages", {})

    product_summary = report_data.get("product_summary", [])
    complaint_counts = report_data.get("complaint_counts", {})
    top_keywords = report_data.get("top_keywords", [])

    positive = int(counts.get("Positive", 0) or 0)
    neutral = int(counts.get("Neutral", 0) or 0)
    negative = int(counts.get("Negative", 0) or 0)

    positive_rate = float(percentages.get("Positive", 0) or 0)
    neutral_rate = float(percentages.get("Neutral", 0) or 0)
    negative_rate = float(percentages.get("Negative", 0) or 0)

    # Handle empty datasets.
    if total <= 0:
        return {
            "method": "Template-based",
            "title": "Executive Summary",
            "overview": "No feedback records are available for analysis.",
            "positive_themes": [],
            "negative_themes": [],
            "complaint_insights": [],
            "product_insights": [],
            "recommendations": [
                "Upload a valid CSV file containing customer feedback."
            ],
            "status": "No data"
        }

    # 1. Overall feedback overview.
    if positive_rate > negative_rate:
        overview = (
            f"Customer feedback is predominantly positive. "
            f"{safe_percentage(positive_rate)} of feedback is positive, "
            f"compared with {safe_percentage(negative_rate)} negative feedback."
        )

    elif negative_rate > positive_rate:
        overview = (
            f"Negative feedback exceeds positive feedback. "
            f"{safe_percentage(negative_rate)} of feedback is negative. "
            f"The business should investigate the recurring concerns."
        )

    else:
        overview = (
            "Positive and negative feedback are at similar levels. "
            "Further investigation is needed to understand customer experience."
        )

    # 2. Complaint category insights.
    sorted_complaints = sorted(
        complaint_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )

    complaint_insights = []

    for category, count in sorted_complaints[:5]:
        count = int(count or 0)

        complaint_insights.append({
            "category": str(category),
            "count": count,
            "message": (
                f"{category} was detected in {count} feedback records. "
                "Review the matching comments to understand the concern."
            )
        })

    # 3. Product performance insights.
    product_insights = []

    for product in product_summary:
        name = product.get("product", "Unknown")
        volume = int(product.get("feedback_count", 0) or 0)

        positive_product = float(
            product.get("positive_rate", 0) or 0
        )

        negative_product = float(
            product.get("negative_rate", 0) or 0
        )

        if volume == 0:
            continue

        if negative_product > positive_product:
            assessment = "Requires attention"
            message = (
                f"{name} has more negative than positive feedback. "
                f"Review its {volume} feedback records before taking action."
            )

        elif positive_product > negative_product:
            assessment = "Positive feedback trend"
            message = (
                f"{name} has more positive than negative feedback "
                f"across {volume} records."
            )

        else:
            assessment = "Mixed feedback"
            message = (
                f"{name} has similar positive and negative feedback "
                f"across {volume} records."
            )

        product_insights.append({
            "product": name,
            "feedback_count": volume,
            "positive_rate": safe_percentage(positive_product),
            "negative_rate": safe_percentage(negative_product),
            "assessment": assessment,
            "message": message
        })

    # 4. Recommendations based on detected evidence.
    recommendations = []

    if negative_rate > positive_rate:
        recommendations.append(
            "Prioritize reviewing negative customer feedback "
            "to identify recurring problems."
        )

    if sorted_complaints:
        category, count = sorted_complaints[0]

        recommendations.append(
            f"Investigate the {category} complaint category, "
            f"which has the highest detected count ({count})."
        )

    attention_products = [
        item for item in product_insights
        if item["assessment"] == "Requires attention"
    ]

    if attention_products:
        names = ", ".join(
            item["product"] for item in attention_products[:3]
        )

        recommendations.append(
            f"Review negative feedback for these products: {names}."
        )

    if not recommendations:
        recommendations.append(
            "Continue monitoring customer feedback "
            "and review individual comments for emerging concerns."
        )

    # 5. Return structured report.
    return {
        "method": "Template-based",
        "title": "Executive Summary",
        "overview": overview,

        "statistics": {
            "total_feedback": total,
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "positive_rate": safe_percentage(positive_rate),
            "neutral_rate": safe_percentage(neutral_rate),
            "negative_rate": safe_percentage(negative_rate)
        },

        "positive_themes": [],
        "negative_themes": [],

        "complaint_insights": complaint_insights,
        "product_insights": product_insights,

        "top_keywords": top_keywords[:10],
        "recommendations": recommendations,

        "status": "Generated"
    }
