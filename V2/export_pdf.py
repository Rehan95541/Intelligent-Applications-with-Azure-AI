"""
PDF export — branded layout with embedded chart images.
"""

from io import BytesIO
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image
)
from reportlab.pdfgen import canvas as _canvas

from chart_images import (
    sentiment_pie_png,
    product_bar_png,
    complaint_bar_png,
)


PRIMARY = HexColor("#4f46e5")
PRIMARY_LIGHT = HexColor("#eef2ff")
TEXT = HexColor("#1e293b")
MUTED = HexColor("#64748b")
BORDER = HexColor("#e2e8f0")
POSITIVE = HexColor("#10b981")
NEUTRAL = HexColor("#f59e0b")
NEGATIVE = HexColor("#ef4444")
BLUE = HexColor("#3b82f6")
WHITE = colors.white


class NumberedCanvas(_canvas.Canvas):
    """Adds page numbers + footer to every page."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_footer(total_pages)
            super().showPage()
        super().save()

    def _draw_footer(self, total_pages):
        self.setFont("Helvetica", 8)
        self.setFillColor(MUTED)
        self.drawString(
            0.7 * inch, 0.5 * inch,
            "Customer Feedback Intelligence — V2"
        )
        self.drawRightString(
            A4[0] - 0.7 * inch, 0.5 * inch,
            f"Page {self._pageNumber} of {total_pages}"
        )
        self.setStrokeColor(BORDER)
        self.setLineWidth(0.5)
        self.line(0.7 * inch, 0.65 * inch, A4[0] - 0.7 * inch, 0.65 * inch)


def _title_bar(text, subtitle=""):
    inner = [Paragraph(
        f'<font color="white" size="22"><b>{text}</b></font>',
        getSampleStyleSheet()["Normal"]
    )]
    if subtitle:
        inner.append(Paragraph(
            f'<font color="#e0e7ff" size="10">{subtitle}</font>',
            getSampleStyleSheet()["Normal"]
        ))

    t = Table([[inner]], colWidths=[A4[0] - 1.4 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def _section_heading(text):
    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        "section_heading",
        parent=styles["Heading2"],
        textColor=PRIMARY,
        fontSize=14,
        spaceBefore=14,
        spaceAfter=8,
        fontName="Helvetica-Bold",
    )
    return Paragraph(text, style)


def _kpi_card_table(items):
    cells = []
    for label, value, color in items:
        hex_color = color.hexval().replace("0x", "#")[:7]
        cell_content = Paragraph(
            f'<font color="#64748b" size="8"><b>{label.upper()}</b></font><br/>'
            f'<font color="{hex_color}" size="20"><b>{value}</b></font>',
            getSampleStyleSheet()["Normal"]
        )
        cells.append(cell_content)

    rows = []
    for i in range(0, len(cells), 4):
        row = cells[i:i + 4]
        while len(row) < 4:
            row.append("")
        rows.append(row)

    col_w = (A4[0] - 1.4 * inch - 0.36 * inch) / 4
    t = Table(rows, colWidths=[col_w] * 4, rowHeights=[0.95 * inch] * len(rows))

    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def _image_from_bytesio(buf, width_inches=5.5):
    """Wrap a PNG BytesIO for reportlab Image with explicit dimensions."""
    buf.seek(0)
    reader = ImageReader(buf)
    iw, ih = reader.getSize()
    aspect = ih / float(iw) if iw else 1.0
    height_inches = width_inches * aspect
    buf.seek(0)
    return Image(buf, width=width_inches * inch, height=height_inches * inch)


def build_pdf(kpis, executive_report):
    """Build the branded PDF. Returns BytesIO."""
    out = BytesIO()
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        topMargin=0.5 * inch, bottomMargin=0.8 * inch,
    )

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "body", parent=styles["BodyText"],
        fontSize=10.5, leading=15, textColor=TEXT,
    )
    rec_style = ParagraphStyle(
        "rec", parent=styles["BodyText"],
        fontSize=10.5, leading=15, textColor=TEXT,
        leftIndent=12, bulletIndent=0, spaceAfter=6,
    )

    story = []

    story.append(_title_bar(
        "Customer Feedback Intelligence",
        f"Executive Report  •  {date.today().strftime('%B %d, %Y')}"
    ))
    story.append(Spacer(1, 16))

    story.append(_section_heading("Overview"))
    story.append(Paragraph(executive_report.get("overview", ""), body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f'<i><font color="#64748b">Method: '
        f'{executive_report.get("method", "Template-based")}</font></i>',
        body_style
    ))
    story.append(Spacer(1, 16))

    story.append(_section_heading("Key Performance Indicators"))
    kpi_items = [
        ("Total Feedback", str(kpis.get("total_feedback", 0)), PRIMARY),
        ("Unique Customers", str(kpis.get("unique_customers", 0)), PRIMARY),
        ("Positive", f"{kpis.get('positive_rate', 0)}%", POSITIVE),
        ("Neutral",  f"{kpis.get('neutral_rate', 0)}%", NEUTRAL),
        ("Negative", f"{kpis.get('negative_rate', 0)}%", NEGATIVE),
        ("Balance", str(kpis.get("sentiment_balance", 0)), PRIMARY),
        ("Avg Score", str(kpis.get("average_sentiment_score", 0)), BLUE),
    ]
    story.append(_kpi_card_table(kpi_items))
    story.append(Spacer(1, 16))

    story.append(_section_heading("Sentiment Distribution"))
    pie_buf = sentiment_pie_png(kpis)
    story.append(_image_from_bytesio(pie_buf, width_inches=4.5))
    story.append(Spacer(1, 12))

    story.append(_section_heading("Product Performance"))
    prod_buf = product_bar_png(kpis)
    story.append(_image_from_bytesio(prod_buf, width_inches=6.0))
    story.append(Spacer(1, 6))

    products = kpis.get("product_summary", [])
    if products:
        rows = [["Product", "Total", "Positive %", "Negative %", "Avg Score"]]
        for p in products:
            rows.append([
                p["product"],
                str(p["total_feedback"]),
                f"{p['positive_rate']}%",
                f"{p['negative_rate']}%",
                str(p["average_sentiment_score"]),
            ])
        t = Table(
            rows,
            colWidths=[2.2 * inch, 1.0 * inch, 1.2 * inch, 1.2 * inch, 1.1 * inch]
        )
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, HexColor("#f8fafc")]),
        ]))
        story.append(t)
    story.append(Spacer(1, 16))

    story.append(_section_heading("Complaint Categories"))
    comp_buf = complaint_bar_png(kpis)
    story.append(_image_from_bytesio(comp_buf, width_inches=6.0))
    story.append(Spacer(1, 12))

    story.append(_section_heading("Recommendations"))
    recs = executive_report.get("recommendations", [])
    if recs:
        for i, rec in enumerate(recs, start=1):
            story.append(Paragraph(f"<b>{i}.</b> {rec}", rec_style))
    else:
        story.append(Paragraph("(none)", body_style))
    story.append(Spacer(1, 16))

    story.append(_section_heading("Limitations & Methodology"))
    limits = [
        "Sentiment: VADER (lightweight English). May misread sarcasm, mixed opinions, Urdu, or Roman Urdu.",
        "Keywords: YAKE statistical extraction — frequency is not confirmation of a problem.",
        "Complaints: Rule-based matching; may miss synonyms and context.",
        "Product comparisons should consider feedback volume.",
        "This report is analysis support — not proof of cause or surveyed CSAT.",
        "Executive summary uses a transparent template method.",
    ]
    for item in limits:
        story.append(Paragraph(f"• {item}", rec_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    out.seek(0)
    return out