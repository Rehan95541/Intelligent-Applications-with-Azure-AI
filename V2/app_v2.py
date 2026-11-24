"""
Customer Feedback Intelligence — V2 application.
"""

import sys
from pathlib import Path

V1_PATH = Path(__file__).resolve().parent.parent / "V1"
sys.path.insert(0, str(V1_PATH))

from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd

from sentiment import SentimentEngine
from keywords import KeywordEngine
from complaints import ComplaintEngine
from analytics import BusinessAnalytics
from insights import generate_executive_summary

from rag_engine import RagEngine
from export_pptx import build_pptx
from export_pdf import build_pdf
from export_csv import build_csv, build_json


_V2_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    static_folder=str(_V2_DIR / "static"),
    template_folder=str(_V2_DIR / "templates"),
)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

REQUIRED_COLUMNS = ["customer_id", "product", "feedback"]


sentiment_engine = SentimentEngine()
keyword_engine = KeywordEngine()
complaint_engine = ComplaintEngine()
analytics_engine = BusinessAnalytics()
rag_engine = RagEngine()


_state = {
    "final_df": None,
    "kpis": None,
    "executive_report": None,
    "backend_info": None,
}


def _process_df(df):
    df.columns = df.columns.str.strip().str.lower()

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

    df = df[REQUIRED_COLUMNS].copy()
    df = df.dropna(subset=["feedback"])

    for col in REQUIRED_COLUMNS:
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

    report_data = {
        "total_feedback": kpis["total_feedback"],
        "sentiment_counts": kpis["sentiment_counts"],
        "sentiment_percentages": kpis["sentiment_percentages"],
        "product_summary": [
            {
                "product": p["product"],
                "feedback_count": p["total_feedback"],
                "positive_rate": p["positive_rate"],
                "negative_rate": p["negative_rate"],
            }
            for p in kpis["product_summary"]
        ],
        "complaint_counts": {c["category"]: c["count"] for c in kpis["complaint_summary"]},
        "top_keywords": [k["keyword"] for k in kpis["top_keywords"]],
    }

    executive_report = generate_executive_summary(report_data)

    return final_df, kpis, executive_report


def _has_data():
    return _state["final_df"] is not None


def _records():
    if not _has_data():
        return []
    return _state["final_df"].to_dict(orient="records")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return render_template("index.html", error="No file was selected.")

    file = request.files["file"]
    if file.filename == "":
        return render_template("index.html", error="Please select a CSV file.")
    if not file.filename.lower().endswith(".csv"):
        return render_template("index.html", error="Only CSV files are supported.")

    try:
        df = pd.read_csv(file)
        final_df, kpis, executive_report = _process_df(df)

        rag_engine.index(final_df)

        _state["final_df"] = final_df
        _state["kpis"] = kpis
        _state["executive_report"] = executive_report
        _state["backend_info"] = {
            "sentiment": sentiment_engine.backend_name,
            "keywords": keyword_engine.backend_name,
            "complaints": complaint_engine.backend_name,
            "analytics": "Pandas",
            "rag": rag_engine.store.backend_name,
            "llm": rag_engine.llm.name,
        }

        return render_template(
            "index.html",
            records=_records(),
            kpis=kpis,
            executive_report=executive_report,
            backend_info=_state["backend_info"],
            rag_filters=rag_engine.available_filters(),
            message="Analysis complete. RAG assistant ready.",
        )

    except UnicodeDecodeError:
        return render_template("index.html", error="Please upload a UTF-8 encoded CSV.")
    except pd.errors.EmptyDataError:
        return render_template("index.html", error="The CSV file is empty.")
    except pd.errors.ParserError:
        return render_template("index.html", error="Invalid CSV format.")
    except Exception as e:
        return render_template("index.html", error=f"Unexpected error: {str(e)}")


@app.route("/ask", methods=["POST"])
def ask():
    if not _has_data():
        return jsonify({"error": "Upload a CSV first."}), 400

    payload = request.get_json(silent=True) or {}
    question = payload.get("question", "").strip()
    filters = payload.get("filters", {})
    top_k = int(payload.get("top_k", 5))
    threshold = float(payload.get("threshold", 0.15))

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    try:
        result = rag_engine.ask(
            question=question,
            filters=filters,
            top_k=top_k,
            threshold=threshold,
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/export/pptx")
def export_pptx():
    if not _has_data():
        return "No analysis available. Upload a CSV first.", 400
    buf = build_pptx(
        _state["kpis"],
        _state["executive_report"],
        _records(),
    )
    return send_file(
        buf,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        as_attachment=True,
        download_name="customer_feedback_report.pptx",
    )


@app.route("/export/pdf")
def export_pdf():
    if not _has_data():
        return "No analysis available. Upload a CSV first.", 400
    buf = build_pdf(_state["kpis"], _state["executive_report"])
    return send_file(
        buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="customer_feedback_report.pdf",
    )


@app.route("/export/csv")
def export_csv():
    if not _has_data():
        return "No analysis available. Upload a CSV first.", 400
    buf = build_csv(_state["final_df"])
    return send_file(
        buf,
        mimetype="text/csv",
        as_attachment=True,
        download_name="customer_feedback_analysis.csv",
    )


@app.route("/export/json")
def export_json():
    if not _has_data():
        return "No analysis available. Upload a CSV first.", 400
    buf = build_json(
        _state["kpis"],
        _state["executive_report"],
        _records(),
    )
    return send_file(
        buf,
        mimetype="application/json",
        as_attachment=True,
        download_name="customer_feedback_analysis.json",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)