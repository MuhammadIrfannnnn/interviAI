from app.models.parsed_resume import ParsedResume
from app.services.ai_service import generate_with_retry


def generate_resume_summary(parsed_resume: ParsedResume) -> str:
    prompt = f"""
Create a very short candidate summary for an AI interviewer.
Max 80 words.
Include only: education, strongest skills, major projects, and experience level if present.
Do not write paragraphs.
Resume:
Name: {parsed_resume.name}
Education: {parsed_resume.education}
Experience: {parsed_resume.experience}
Skills: {parsed_resume.skills}
Projects: {parsed_resume.projects}
"""

    return generate_with_retry(prompt)