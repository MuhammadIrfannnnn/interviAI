from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)

from app.models.interview_session import InterviewSession

# ---------------------------------------------------------------------------
# Brand palette — matches the InterviAI frontend's cyan accent, adapted for a
# light/print-friendly document rather than the app's dark theme.
# ---------------------------------------------------------------------------
ACCENT = colors.HexColor("#0E7490")       # cyan-700, primary accent
ACCENT_SOFT = colors.HexColor("#ECFEFF")  # cyan-50, header background
TEXT_PRIMARY = colors.HexColor("#111827")
TEXT_SECONDARY = colors.HexColor("#4B5563")
TEXT_MUTED = colors.HexColor("#9CA3AF")
BORDER = colors.HexColor("#E5E7EB")

STRONG = colors.HexColor("#16A34A")   # green
AVERAGE = colors.HexColor("#D97706")  # amber
WEAK = colors.HexColor("#DC2626")     # red
NEUTRAL = colors.HexColor("#6B7280")  # gray, fallback for unrecognized labels


def _level_color(level: str) -> colors.Color:
    """Maps a competency level or recommendation string to a badge color.
    Falls back to NEUTRAL for any label not recognized, so new backend
    values never crash rendering — they just render gray instead of
    silently looking "strong" or "weak" when they're neither.
    """
    normalized = (level or "").strip().lower()
    if normalized in ("strong", "hire", "strong hire"):
        return STRONG
    if normalized in ("average", "moderate", "developing"):
        return AVERAGE
    if normalized in ("weak", "poor", "no hire", "strong no hire"):
        return WEAK
    return NEUTRAL


def _score_color(score: float) -> colors.Color:
    """Assumes a 0–10 scale, consistent with the scores seen in practice
    (e.g. 8.7, 8.5). Adjust thresholds here if the backend's scale changes.
    """
    if score >= 8:
        return STRONG
    if score >= 6:
        return AVERAGE
    return WEAK


def _build_styles():
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            textColor=ACCENT,
            fontSize=22,
            spaceAfter=2,
            alignment=TA_LEFT,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=base["Normal"],
            textColor=TEXT_MUTED,
            fontSize=9,
        ),
        "header_field_label": ParagraphStyle(
            "HeaderFieldLabel",
            parent=base["Normal"],
            textColor=TEXT_MUTED,
            fontSize=8,
            spaceAfter=1,
        ),
        "header_field_value": ParagraphStyle(
            "HeaderFieldValue",
            parent=base["Normal"],
            textColor=TEXT_PRIMARY,
            fontSize=11,
            fontName="Helvetica-Bold",
        ),
        "section_title": ParagraphStyle(
            "SectionTitle",
            parent=base["Heading2"],
            textColor=TEXT_PRIMARY,
            fontSize=13,
            spaceBefore=4,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            textColor=TEXT_SECONDARY,
            fontSize=10,
            leading=15,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            textColor=TEXT_SECONDARY,
            fontSize=10,
            leading=15,
            leftIndent=12,
            spaceAfter=4,
        ),
        "competency_name": ParagraphStyle(
            "CompetencyName",
            parent=base["Normal"],
            textColor=TEXT_PRIMARY,
            fontSize=11,
            fontName="Helvetica-Bold",
        ),
        "score_label": ParagraphStyle(
            "ScoreLabel",
            parent=base["Normal"],
            textColor=TEXT_MUTED,
            fontSize=8,
            alignment=TA_CENTER,
        ),
        "score_value": ParagraphStyle(
            "ScoreValue",
            parent=base["Normal"],
            fontSize=16,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
        ),
    }
    return styles


def _section_divider():
    return HRFlowable(width="100%", thickness=1, color=BORDER, spaceBefore=2, spaceAfter=10)


def _badge_table(text: str, color: colors.Color, styles):
    """A small pill-style badge (colored border + text), used for the
    recommendation and for each competency's level.
    """
    style = ParagraphStyle(
        "BadgeText",
        parent=styles["body"],
        textColor=color,
        fontName="Helvetica-Bold",
        fontSize=9,
    )
    t = Table([[Paragraph(text, style)]], colWidths=None)
    t.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, color),
                ("BACKGROUND", (0, 0), (-1, -1), colors.Color(color.red, color.green, color.blue, alpha=0.08)),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return t


def _header_block(session: InterviewSession, report: dict, styles):
    """Candidate/session identity block — previously missing entirely,
    which made the PDF impossible to identify once separated from the app.
    """
    # NOTE: adjust these attribute paths to match your actual User model
    # relationship if different (e.g. session.candidate.full_name).
    candidate_name = getattr(getattr(session, "user", None), "full_name", None) or "—"
    candidate_email = getattr(getattr(session, "user", None), "email", None) or "—"

    started_at = getattr(session, "started_at", None)
    date_str = started_at.strftime("%B %d, %Y") if isinstance(started_at, datetime) else "—"

    left = [
        Paragraph("InterviAI Interview Report", styles["title"]),
        Paragraph("AI-powered mock interview assessment", styles["subtitle"]),
    ]

    field_rows = [
        [
            Paragraph("CANDIDATE", styles["header_field_label"]),
            Paragraph("ROLE", styles["header_field_label"]),
            Paragraph("DIFFICULTY", styles["header_field_label"]),
            Paragraph("DATE", styles["header_field_label"]),
        ],
        [
            Paragraph(candidate_name, styles["header_field_value"]),
            Paragraph(session.role_applied, styles["header_field_value"]),
            Paragraph(session.difficulty, styles["header_field_value"]),
            Paragraph(date_str, styles["header_field_value"]),
        ],
    ]
    field_table = Table(field_rows, colWidths=[1.7 * inch] * 4)
    field_table.setStyle(
        TableStyle(
            [
                ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                ("TOPPADDING", (0, 1), (-1, 1), 0),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
            ]
        )
    )

    header_table = Table(
        [[left, ""]],
        colWidths=[4.5 * inch, 2.2 * inch],
    )
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, -1), ACCENT_SOFT),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    return [header_table, Spacer(1, 6), field_table, Spacer(1, 4),
            _padded(candidate_email, styles), Spacer(1, 18)]


def _padded(email: str, styles):
    return Table(
        [[Paragraph(email, styles["subtitle"])]],
        colWidths=[6.7 * inch],
        style=TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 16)]),
    )


def _score_row(report: dict, styles):
    """Scores as colored cards in a single row instead of a flat bulleted
    list — makes the overall shape of a candidate's performance readable
    at a glance.
    """
    entries = [
        ("Overall", report["overall_score"]),
        ("Technical", report["technical_score"]),
        ("Communication", report["communication_score"]),
        ("Confidence", report["confidence_score"]),
        ("Problem Solving", report["problem_solving_score"]),
    ]

    cells = []
    for label, value in entries:
        color = _score_color(value)
        value_style = ParagraphStyle("ScoreVal", parent=styles["score_value"], textColor=color)
        cell_content = [
            Paragraph(f"{value:.1f}", value_style),
            Spacer(1, 4),
            Paragraph(label.upper(), styles["score_label"]),
        ]
        cells.append(cell_content)

    t = Table([cells], colWidths=[1.34 * inch] * len(entries))
    t.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 1, BORDER),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return t


def _competency_card(competency: dict, styles):
    color = _level_color(competency["level"])
    name = competency["competency"].replace("_", " ").title()

    row = Table(
        [[Paragraph(name, styles["competency_name"]), _badge_table(competency["level"], color, styles)]],
        colWidths=[4.5 * inch, 2.2 * inch],
    )
    row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))

    return KeepTogether(
        [
            row,
            Spacer(1, 3),
            Paragraph(competency["summary"], styles["body"]),
            Spacer(1, 12),
        ]
    )


def generate_interview_report_pdf(session: InterviewSession, report: dict):
    styles = _build_styles()

    output_dir = Path("generated_reports")
    output_dir.mkdir(exist_ok=True)
    pdf_path = output_dir / f"interview_report_{session.id}.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        topMargin=0.5 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
    )

    elements = []

    # --- Header: branding + candidate/role/difficulty/date ---
    elements += _header_block(session, report, styles)

    # --- Recommendation badge ---
    elements.append(
        KeepTogether(
            [
                Paragraph("RECOMMENDATION", styles["header_field_label"]),
                Spacer(1, 3),
                _badge_table(report["recommendation"], _level_color(report["recommendation"]), styles),
                Spacer(1, 16),
            ]
        )
    )

    # --- Scores ---
    elements.append(Paragraph("Scores", styles["section_title"]))
    elements.append(_score_row(report, styles))
    elements.append(Spacer(1, 10))
    elements.append(_section_divider())

    # --- Bulleted sections ---
    for title, key in [
        ("Strengths", "strengths"),
        ("Weaknesses", "weaknesses"),
        ("Highlights", "highlights"),
        ("Concerns", "concerns"),
        ("Technical Evidence", "technical_evidence"),
        ("Learning Roadmap", "learning_roadmap"),
    ]:
        items = report.get(key) or []
        if not items:
            continue
        elements.append(Paragraph(title, styles["section_title"]))
        for item in items:
            elements.append(Paragraph(f"•  {item}", styles["bullet"]))
        elements.append(Spacer(1, 8))
        elements.append(_section_divider())

    # --- Competency report ---
    elements.append(Paragraph("Competency Report", styles["section_title"]))
    for competency in report["competency_reports"]:
        elements.append(_competency_card(competency, styles))
    elements.append(_section_divider())

    # --- Overall feedback ---
    elements.append(Paragraph("Overall Feedback", styles["section_title"]))
    elements.append(Paragraph(report["overall_feedback"], styles["body"]))

    doc.build(elements)

    return pdf_path