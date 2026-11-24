"""
Chart image generator for PDF export.

Uses matplotlib (Agg backend, no GUI) to render PNG bytes in memory.
"""

from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from matplotlib import rcParams

rcParams["font.family"] = "DejaVu Sans"
rcParams["axes.edgecolor"] = "#e2e8f0"
rcParams["axes.labelcolor"] = "#64748b"
rcParams["xtick.color"] = "#64748b"
rcParams["ytick.color"] = "#64748b"


POSITIVE_COLOR = "#10b981"
NEUTRAL_COLOR = "#f59e0b"
NEGATIVE_COLOR = "#ef4444"
PRIMARY_COLOR = "#4f46e5"
BLUE_COLOR = "#3b82f6"


def sentiment_pie_png(kpis):
    counts = kpis.get("sentiment_counts", {})
    values = [
        counts.get("Positive", 0),
        counts.get("Neutral", 0),
        counts.get("Negative", 0),
    ]

    if sum(values) == 0:
        return _empty_png("No sentiment data")

    fig, ax = plt.subplots(figsize=(5, 4), dpi=120)
    colors = [POSITIVE_COLOR, NEUTRAL_COLOR, NEGATIVE_COLOR]
    labels = ["Positive", "Neutral", "Negative"]

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
        colors=colors,
        startangle=90,
        wedgeprops={"width": 0.45, "edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 11, "color": "#334155"},
    )

    for at in autotexts:
        at.set_color("white")
        at.set_fontweight("bold")
        at.set_fontsize(10)

    ax.set_title("Sentiment Distribution", fontsize=13, fontweight="bold", color="#1e293b")
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def product_bar_png(kpis):
    products = kpis.get("product_summary", [])
    if not products:
        return _empty_png("No product data")

    names = [p["product"] for p in products]
    positives = [p["positive"] for p in products]
    negatives = [p["negative"] for p in products]

    fig, ax = plt.subplots(figsize=(6, 4), dpi=120)
    y_pos = range(len(names))
    bar_h = 0.38

    ax.barh(
        [y - bar_h / 2 for y in y_pos], positives,
        height=bar_h, color=POSITIVE_COLOR, label="Positive"
    )
    ax.barh(
        [y + bar_h / 2 for y in y_pos], negatives,
        height=bar_h, color=NEGATIVE_COLOR, label="Negative"
    )

    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(names, fontsize=10, color="#334155")
    ax.invert_yaxis()
    ax.set_xlabel("Review count", fontsize=10)
    ax.set_title("Product Sentiment", fontsize=13, fontweight="bold", color="#1e293b")
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    ax.grid(axis="x", color="#e2e8f0", linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def complaint_bar_png(kpis):
    complaints = kpis.get("complaint_summary", [])
    if not complaints:
        return _empty_png("No complaint data")

    names = [c["category"] for c in complaints]
    counts = [c["count"] for c in complaints]

    fig, ax = plt.subplots(figsize=(6, 3.8), dpi=120)
    bars = ax.bar(names, counts, color=BLUE_COLOR, edgecolor="#2563eb", linewidth=1)

    ax.set_ylabel("Count", fontsize=10)
    ax.set_title("Complaint Categories", fontsize=13, fontweight="bold", color="#1e293b")
    ax.tick_params(axis="x", rotation=20, labelsize=9)
    ax.grid(axis="y", color="#e2e8f0", linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(counts) * 0.02,
            str(count),
            ha="center", va="bottom", fontsize=9, color="#334155"
        )

    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def _empty_png(message):
    fig, ax = plt.subplots(figsize=(4, 2.5), dpi=100)
    ax.text(0.5, 0.5, message, ha="center", va="center",
            fontsize=12, color="#94a3b8", transform=ax.transAxes)
    ax.axis("off")
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf