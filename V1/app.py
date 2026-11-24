from flask import Flask, render_template, request
import pandas as pd
from insights import generate_executive_summary
from sentiment import SentimentEngine
from keywords import KeywordEngine
from complaints import ComplaintEngine
from analytics import BusinessAnalytics


app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

REQUIRED_COLUMNS = [
    "customer_id",
    "product",
    "feedback"
]


# Initialize engines
sentiment_engine = SentimentEngine()
keyword_engine = KeywordEngine()
complaint_engine = ComplaintEngine()
analytics_engine = BusinessAnalytics()


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:

        return render_template(
            "index.html",
            error="No file was selected."
        )

    file = request.files["file"]

    if file.filename == "":

        return render_template(
            "index.html",
            error="Please select a CSV file."
        )

    if not file.filename.lower().endswith(".csv"):

        return render_template(
            "index.html",
            error="Only CSV files are supported."
        )

    try:

        # -----------------------------
        # 1. Read and validate CSV
        # -----------------------------

        df = pd.read_csv(file)

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )

        missing = [
            col for col in REQUIRED_COLUMNS
            if col not in df.columns
        ]

        if missing:

            return render_template(
                "index.html",
                error=f"Missing columns: {', '.join(missing)}"
            )

        df = df[REQUIRED_COLUMNS].copy()

        df = df.dropna(subset=["feedback"])

        for column in REQUIRED_COLUMNS:

            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        df = df[df["feedback"] != ""]

        if df.empty:

            return render_template(
                "index.html",
                error="No valid feedback records found."
            )

        # -----------------------------
        # 2. Sentiment analysis
        # -----------------------------

        sentiment_results = df["feedback"].apply(
            sentiment_engine.analyze
        )

        sentiment_df = pd.DataFrame(
            sentiment_results.tolist()
        )

        # -----------------------------
        # 3. Keyword extraction
        # -----------------------------

        df["keywords"] = df["feedback"].apply(
            keyword_engine.extract
        )

        # -----------------------------
        # 4. Complaint categorization
        # -----------------------------

        df["complaint_categories"] = df["feedback"].apply(
            complaint_engine.categorize
        )

        # -----------------------------
        # 5. Combine results
        # -----------------------------

        final_df = pd.concat(
            [
                df.reset_index(drop=True),
                sentiment_df.reset_index(drop=True)
            ],
            axis=1
        )

        # -----------------------------
        # 6. Business analytics
        # -----------------------------

        kpis = analytics_engine.calculate(final_df)

        # -----------------------------
        # 7. Executive summary (Step 9)
        # -----------------------------

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

        top_keyword_names = [
            item["keyword"]
            for item in kpis["top_keywords"]
        ]

        report_data = {
            "total_feedback": kpis["total_feedback"],
            "sentiment_counts": kpis["sentiment_counts"],
            "sentiment_percentages": kpis["sentiment_percentages"],
            "product_summary": product_summary_for_report,
            "complaint_counts": complaint_counts,
            "top_keywords": top_keyword_names
        }

        executive_report = generate_executive_summary(report_data)

        # -----------------------------
        # 8. Prepare frontend records
        # -----------------------------

        records = final_df.to_dict(
            orient="records"
        )

        # -----------------------------
        # 9. Backend identification
        # -----------------------------

        backend_info = {

            "sentiment": sentiment_engine.backend_name,

            "keywords": keyword_engine.backend_name,

            "complaints": complaint_engine.backend_name,

            "analytics": "Pandas"

        }

        return render_template(

            "index.html",

            records=records,

            kpis=kpis,

            backend_info=backend_info,

            executive_report=executive_report,

            message="Business intelligence analysis completed!"

        )

    except UnicodeDecodeError:

        error = "Please upload a UTF-8 encoded CSV."

    except pd.errors.EmptyDataError:

        error = "The CSV file is empty."

    except pd.errors.ParserError:

        error = "Invalid CSV format."

    except Exception as e:

        error = f"Unexpected error: {str(e)}"

    return render_template(
        "index.html",
        error=error
    )


if __name__ == "__main__":

    app.run(debug=True)