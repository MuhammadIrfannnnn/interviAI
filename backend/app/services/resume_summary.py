from app.models.parsed_resume import ParsedResume
from app.services.ai_service import client, MODEL


def generate_resume_summary(parsed_resume: ParsedResume) -> str:
    prompt = f"""
You are preparing a concise candidate profile for an AI interviewer.

Summarize this resume into a maximum of 200 words.

Include only:
- Education
- Core technical skills
- Relevant experience
- Major projects
- Strong areas
- Any notable achievements

Do NOT copy everything.
Remove unnecessary details.
Return plain text only.

Resume:

Name:
{parsed_resume.name}

Education:
{parsed_resume.education}

Experience:
{parsed_resume.experience}

Skills:
{parsed_resume.skills}

Projects:
{parsed_resume.projects}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    if not response.text:
        raise ValueError("Gemini returned an empty resume summary.")

    return response.text.strip()