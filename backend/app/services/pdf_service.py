from pathlib import Path
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph,SimpleDocTemplate,Spacer
from app.models.interview_session import InterviewSession

def generate_interview_report_pdf(session:InterviewSession,report:dict):
    styles = getSampleStyleSheet()
    output_dir = Path("generated_reports")
    output_dir.mkdir(exist_ok=True)
    pdf_path = output_dir / f"interview_report_{session.id}.pdf"
    doc = SimpleDocTemplate(str(pdf_path))
    elements = []
    elements.append(
    Paragraph(
        "<b>InterviAI Interview Report</b>",
        styles["Title"],))
    elements.append(Spacer(1, 20))

    elements.append(
    Paragraph(
        f"<b>Role:</b> {session.role_applied}",
        styles["Normal"],
    ))

    elements.append(
        Paragraph(
            f"<b>Difficulty:</b> {session.difficulty}",
            styles["Normal"],
        ))

    elements.append(
        Paragraph(
            f"<b>Overall Score:</b> {report['overall_score']}",
            styles["Normal"],
        ))

    elements.append(Spacer(1, 20))

    elements.append(
    Paragraph(
        f"<b>Recommendation:</b> {report['recommendation']}",
        styles["Heading2"],
    ))

    elements.append(
    Paragraph(
        "<b>Scores</b>",
        styles["Heading2"],
    ))

    scores = [
        ("Technical", report["technical_score"]),
        ("Communication", report["communication_score"]),
        ("Confidence", report["confidence_score"]),
        ("Problem Solving", report["problem_solving_score"]),
    ]

    for title, value in scores:
        elements.append(
            Paragraph(
                f"{title}: {value}",
                styles["Normal"],
            ))

    elements.append(Spacer(1, 20))

    def add_list(title, items):
        elements.append(
            Paragraph(
                f"<b>{title}</b>",
                styles["Heading2"],
            ))
        for item in items:
            elements.append(
                Paragraph(
                    f"• {item}",
                    styles["Normal"],
                ))
        elements.append(Spacer(1, 15))

    add_list("Strengths", report["strengths"])
    add_list("Weaknesses", report["weaknesses"])
    add_list("Highlights", report["highlights"])
    add_list("Concerns", report["concerns"])
    add_list("Technical Evidence", report["technical_evidence"])
    add_list("Learning Roadmap", report["learning_roadmap"])

    elements.append(
    Paragraph(
        "<b>Competency Report</b>",
        styles["Heading2"],
    ))
    for competency in report["competency_reports"]:
        elements.append(
            Paragraph(
                f"<b>{competency['competency']}</b>",
                styles["Heading3"],
            ))
        elements.append(
            Paragraph(
                f"Level: {competency['level']}",
                styles["Normal"],
            ))
        elements.append(
            Paragraph(
                competency["summary"],
                styles["Normal"],
            ))
        elements.append(Spacer(1, 10))


    elements.append(
    Paragraph(
        "<b>Overall Feedback</b>",
        styles["Heading2"],
    ))
    elements.append(
        Paragraph(
            report["overall_feedback"],
            styles["Normal"],
        ))
    doc.build(elements)

    return pdf_path
