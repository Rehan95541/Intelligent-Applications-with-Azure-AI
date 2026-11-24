"""
PowerPoint export — 8 branded slides with native PPTX charts.
"""

from io import BytesIO
from datetime import date

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION


PRIMARY = RGBColor(0x4F, 0x46, 0xE5)
PRIMARY_DARK = RGBColor(0x37, 0x33, 0xC6)
PRIMARY_LIGHT = RGBColor(0xEE, 0xF2, 0xFF)
TEXT = RGBColor(0x1E, 0x29, 0x3B)
MUTED = RGBColor(0x64, 0x74, 0x8B)
BORDER = RGBColor(0xE2, 0xE8, 0xF0)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
POSITIVE = RGBColor(0x10, 0xB9, 0x81)
NEUTRAL = RGBColor(0xF5, 0x9E, 0x0B)
NEGATIVE = RGBColor(0xEF, 0x44, 0x44)
BLUE = RGBColor(0x3B, 0x82, 0xF6)


def _add_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.7)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = PRIMARY
    bar.line.fill.background()

    footer = slide.shapes.add_textbox(
        Inches(0.5), prs.slide_height - Inches(0.45), Inches(9), Inches(0.3)
    )
    tf = footer.text_frame
    tf.text = "Customer Feedback Intelligence — V2"
    p = tf.paragraphs[0]
    p.font.size = Pt(9)
    p.font.color.rgb = MUTED

    pageno = slide.shapes.add_textbox(
        prs.slide_width - Inches(1.2), prs.slide_height - Inches(0.45),
        Inches(0.9), Inches(0.3)
    )
    tf2 = pageno.text_frame
    tf2.text = str(len(prs.slides))
    p2 = tf2.paragraphs[0]
    p2.font.size = Pt(9)
    p2.font.color.rgb = MUTED
    p2.alignment = PP_ALIGN.RIGHT

    return slide


def _title(slide, text, top=0.95):
    box = slide.shapes.add_textbox(Inches(0.6), Inches(top), Inches(9), Inches(0.7))
    tf = box.text_frame
    tf.text = text
    p = tf.paragraphs[0]
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.font.name = "Calibri"
    return box


def _subtitle(slide, text, top=1.6):
    box = slide.shapes.add_textbox(Inches(0.6), Inches(top), Inches(9), Inches(0.5))
    tf = box.text_frame
    tf.text = text
    p = tf.paragraphs[0]
    p.font.size = Pt(13)
    p.font.color.rgb = MUTED
    return box


def _body(slide, text, top=2.0, height=4.5, size=13):
    box = slide.shapes.add_textbox(
        Inches(0.6), Inches(top), Inches(9), Inches(height)
    )
    tf = box.text_frame
    tf.word_wrap = True
    tf.text = text
    for p in tf.paragraphs:
        p.font.size = Pt(size)
        p.font.color.rgb = TEXT
    return box


def _bullets(slide, items, top=2.0, size=13, left=0.6, width=9):
    box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(4.6)
    )
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(size)
        p.font.color.rgb = TEXT
        p.space_after = Pt(8)
    return box


def _kpi_card(slide, x, y, w, h, label, value, accent=PRIMARY):
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    card.fill.solid()
    card.fill.fore_color.rgb = WHITE
    card.line.color.rgb = BORDER
    card.line.width = Pt(0.75)

    accent_bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.08)
    )
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = accent
    accent_bar.line.fill.background()

    lbl_box = slide.shapes.add_textbox(
        Inches(x + 0.15), Inches(y + 0.15), Inches(w - 0.3), Inches(0.35)
    )
    tf = lbl_box.text_frame
    tf.text = label.upper()
    p = tf.paragraphs[0]
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = MUTED

    val_box = slide.shapes.add_textbox(
        Inches(x + 0.15), Inches(y + 0.45), Inches(w - 0.3), Inches(0.6)
    )
    tf2 = val_box.text_frame
    tf2.text = str(value)
    p2 = tf2.paragraphs[0]
    p2.font.size = Pt(24)
    p2.font.bold = True
    p2.font.color.rgb = TEXT


def _style_chart(chart, has_legend=True):
    chart.font.size = Pt(10)
    chart.font.name = "Calibri"
    chart.font.color.rgb = TEXT
    if has_legend:
        chart.has_legend = True
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
        chart.legend.font.size = Pt(10)
    else:
        chart.has_legend = False


def _slide_title(prs, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = PRIMARY
    bg.line.fill.background()

    stripe = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(4.5), prs.slide_width, Inches(0.15)
    )
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = PRIMARY_LIGHT
    stripe.line.fill.background()

    title_box = slide.shapes.add_textbox(
        Inches(1), Inches(2.5), Inches(8), Inches(1.2)
    )
    tf = title_box.text_frame
    tf.text = "Customer Feedback Intelligence"
    p = tf.paragraphs[0]
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

    sub_box = slide.shapes.add_textbox(
        Inches(1), Inches(3.7), Inches(8), Inches(0.6)
    )
    tf2 = sub_box.text_frame
    tf2.text = f"Executive Report — {total} feedback records analyzed"
    p2 = tf2.paragraphs[0]
    p2.font.size = Pt(16)
    p2.font.color.rgb = PRIMARY_LIGHT
    p2.alignment = PP_ALIGN.CENTER

    date_box = slide.shapes.add_textbox(
        Inches(1), Inches(4.8), Inches(8), Inches(0.4)
    )
    tf3 = date_box.text_frame
    tf3.text = date.today().strftime("%B %d, %Y")
    p3 = tf3.paragraphs[0]
    p3.font.size = Pt(12)
    p3.font.color.rgb = WHITE
    p3.alignment = PP_ALIGN.CENTER


def _slide_exec(prs, report):
    slide = _add_slide(prs)
    _title(slide, "Executive Summary")

    method = report.get("method", "Template-based")
    badge = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(7.4), Inches(1.05), Inches(2.1), Inches(0.4)
    )
    badge.fill.solid()
    badge.fill.fore_color.rgb = PRIMARY_LIGHT
    badge.line.color.rgb = PRIMARY
    badge.line.width = Pt(0.5)
    tf = badge.text_frame
    tf.text = method
    p = tf.paragraphs[0]
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.alignment = PP_ALIGN.CENTER

    overview = report.get("overview", "")
    _body(slide, overview, top=1.6, height=2.5, size=14)

    stats = report.get("statistics", {})
    if stats:
        _subtitle(slide, "Key statistics", top=4.2)
        cards = [
            ("Total", str(stats.get("total_feedback", 0)), PRIMARY),
            ("Positive", stats.get("positive_rate", "0%"), POSITIVE),
            ("Neutral",  stats.get("neutral_rate", "0%"), NEUTRAL),
            ("Negative", stats.get("negative_rate", "0%"), NEGATIVE),
        ]
        x = 0.6
        for label, val, color in cards:
            _kpi_card(slide, x, 4.65, 2.15, 1.15, label, val, accent=color)
            x += 2.3


def _slide_kpis(prs, kpis):
    slide = _add_slide(prs)
    _title(slide, "Key Performance Indicators")

    cards = [
        ("Total Feedback", kpis.get("total_feedback", 0), PRIMARY),
        ("Unique Customers", kpis.get("unique_customers", 0), PRIMARY),
        ("Positive", f"{kpis.get('positive_rate', 0)}%", POSITIVE),
        ("Neutral",  f"{kpis.get('neutral_rate', 0)}%", NEUTRAL),
        ("Negative", f"{kpis.get('negative_rate', 0)}%", NEGATIVE),
        ("Balance", kpis.get("sentiment_balance", 0), PRIMARY),
        ("Avg Score", kpis.get("average_sentiment_score", 0), BLUE),
    ]

    row1 = cards[:4]
    row2 = cards[4:]
    x = 0.6
    for label, val, color in row1:
        _kpi_card(slide, x, 1.5, 2.15, 1.6, label, val, accent=color)
        x += 2.3
    x = 0.6
    for label, val, color in row2:
        _kpi_card(slide, x, 3.5, 2.15, 1.6, label, val, accent=color)
        x += 2.3


def _slide_sentiment(prs, kpis):
    slide = _add_slide(prs)
    _title(slide, "Sentiment Distribution")

    counts = kpis.get("sentiment_counts", {})
    values = [
        counts.get("Positive", 0),
        counts.get("Neutral", 0),
        counts.get("Negative", 0),
    ]

    chart_data = CategoryChartData()
    chart_data.categories = ["Positive", "Neutral", "Negative"]
    chart_data.add_series("Sentiment", values)

    chart_shape = slide.shapes.add_chart(
        XL_CHART_TYPE.DOUGHNUT,
        Inches(1.5), Inches(1.4), Inches(7), Inches(5),
        chart_data
    )
    chart = chart_shape.chart
    _style_chart(chart, has_legend=True)

    plot = chart.plots[0]
    points = plot.series[0].points
    for i, color in enumerate([POSITIVE, NEUTRAL, NEGATIVE]):
        if i < len(points):
            points[i].format.fill.solid()
            points[i].format.fill.fore_color.rgb = color

    plot.has_data_labels = True
    plot.data_labels.show_percentage = True
    plot.data_labels.show_value = False
    plot.data_labels.number_format = "0.0%"
    plot.data_labels.font.size = Pt(11)
    plot.data_labels.font.bold = True
    plot.data_labels.font.color.rgb = WHITE


def _slide_products(prs, kpis):
    slide = _add_slide(prs)
    _title(slide, "Product Performance")

    products = kpis.get("product_summary", [])
    if not products:
        _body(slide, "No product data available.", top=1.6)
        return

    chart_data = CategoryChartData()
    chart_data.categories = [p["product"] for p in products]
    chart_data.add_series("Positive", [p["positive"] for p in products])
    chart_data.add_series("Negative", [p["negative"] for p in products])

    chart_shape = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED,
        Inches(0.6), Inches(1.4), Inches(9), Inches(3.3),
        chart_data
    )
    chart = chart_shape.chart
    _style_chart(chart, has_legend=True)

    series = chart.plots[0].series
    series[0].format.fill.solid()
    series[0].format.fill.fore_color.rgb = POSITIVE
    series[1].format.fill.solid()
    series[1].format.fill.fore_color.rgb = NEGATIVE

    rows = len(products) + 1
    table_shape = slide.shapes.add_table(
        rows, 5,
        Inches(0.6), Inches(4.9), Inches(9), Inches(1.8)
    )
    table = table_shape.table
    headers = ["Product", "Total", "Pos %", "Neg %", "Avg"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = WHITE
        cell.fill.solid()
        cell.fill.fore_color.rgb = PRIMARY

    for ri, prod in enumerate(products, start=1):
        vals = [
            prod["product"],
            str(prod["total_feedback"]),
            f"{prod['positive_rate']}%",
            f"{prod['negative_rate']}%",
            str(prod["average_sentiment_score"]),
        ]
        for ci, v in enumerate(vals):
            cell = table.cell(ri, ci)
            cell.text = v
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.font.color.rgb = TEXT


def _slide_complaints(prs, kpis):
    slide = _add_slide(prs)
    _title(slide, "Complaint Categories")

    complaints = kpis.get("complaint_summary", [])
    if not complaints:
        _body(slide, "No complaint categories detected.", top=1.6)
        return

    top = complaints[:8]
    chart_data = CategoryChartData()
    chart_data.categories = [c["category"] for c in top]
    chart_data.add_series("Count", [c["count"] for c in top])

    chart_shape = slide.shapes.add_chart(
        XL_CHART_TYPE.BAR_CLUSTERED,
        Inches(0.6), Inches(1.4), Inches(9), Inches(5.2),
        chart_data
    )
    chart = chart_shape.chart
    _style_chart(chart, has_legend=False)

    series = chart.plots[0].series[0]
    series.format.fill.solid()
    series.format.fill.fore_color.rgb = BLUE

    chart.plots[0].has_data_labels = True
    chart.plots[0].data_labels.font.size = Pt(10)
    chart.plots[0].data_labels.font.bold = True
    chart.plots[0].data_labels.position = XL_LABEL_POSITION.OUTSIDE_END


def _slide_keywords_recs(prs, kpis, report):
    slide = _add_slide(prs)
    _title(slide, "Keywords & Recommendations")

    keywords = kpis.get("top_keywords", [])[:8]
    if keywords:
        _subtitle(slide, "Top keywords", top=1.5)
        kw_box = slide.shapes.add_textbox(
            Inches(0.6), Inches(1.95), Inches(4.3), Inches(4.5)
        )
        tf = kw_box.text_frame
        tf.word_wrap = True
        for i, k in enumerate(keywords):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = f"{k['keyword']}  ({k['count']})"
            p.font.size = Pt(13)
            p.font.color.rgb = TEXT
            p.space_after = Pt(6)
    else:
        _subtitle(slide, "Top keywords", top=1.5)
        _body(slide, "(none)", top=1.95, height=1, size=12)

    recs = report.get("recommendations", [])
    _subtitle(slide, "Recommendations", top=1.5)
    rec_box = slide.shapes.add_textbox(
        Inches(5.2), Inches(1.95), Inches(4.4), Inches(4.5)
    )
    tf = rec_box.text_frame
    tf.word_wrap = True
    if recs:
        for i, rec in enumerate(recs, start=1):
            p = tf.paragraphs[0] if i == 1 else tf.add_paragraph()
            p.text = f"{i}. {rec}"
            p.font.size = Pt(12)
            p.font.color.rgb = TEXT
            p.space_after = Pt(8)
    else:
        p = tf.paragraphs[0]
        p.text = "(none)"
        p.font.size = Pt(12)
        p.font.color.rgb = MUTED


def _slide_limitations(prs):
    slide = _add_slide(prs)
    _title(slide, "Limitations & Methodology")

    items = [
        "Sentiment: VADER (lightweight English). May misread sarcasm, mixed opinions, Urdu, or Roman Urdu.",
        "Keywords: YAKE statistical extraction — frequency is not confirmation of a problem.",
        "Complaints: Rule-based matching; may miss synonyms and context.",
        "Product comparisons should consider feedback volume — small samples are noisy.",
        "This report is analysis support — not proof of cause or surveyed CSAT.",
        "RAG answers are grounded in the uploaded reviews — no external knowledge used.",
        "Executive summary uses a transparent template method — not a generative model.",
    ]
    _bullets(slide, items, top=1.6, size=12)


def build_pptx(kpis, executive_report, records):
    """Build the branded 8-slide deck. Returns BytesIO."""
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    total = kpis.get("total_feedback", 0)

    _slide_title(prs, total)
    _slide_exec(prs, executive_report)
    _slide_kpis(prs, kpis)
    _slide_sentiment(prs, kpis)
    _slide_products(prs, kpis)
    _slide_complaints(prs, kpis)
    _slide_keywords_recs(prs, kpis, executive_report)
    _slide_limitations(prs)

    buf = BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf