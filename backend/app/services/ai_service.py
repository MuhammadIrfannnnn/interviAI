from app.schemas.resume import ParsedResume
from google import genai
from app.core.config import settings
import json

client=genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL="gemini-2.5-flash"

def parse_resume(text:str)->ParsedResume:
    prompt = f"""
You are an expert resume parser.

Extract the following fields:

- name:str
- email:str
- skills:List[str]
- education:List[str]
- experience:List[str]
- projects:List[str]

Return ONLY a valid JSON object.

Do NOT include:

- markdown
- triple backticks
- explanations
- comments
- headings

Resume:

{text}
"""
    response=client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    print("Gemini Response")
    print(response.text)
    print("------------------------------------------------------------")
    response_text=response.text.strip()
    if response_text.startswith("```json"):
        response_text=response_text.replace("```json","",1)
    if response_text.endswith("```"):
        response_text=response_text[:-3]
    response_text=response_text.strip()
    try:
        data = json.loads(response_text)
        return ParsedResume(**data)
    except json.JSONDecodeError:
        print("Gemini returned invalid JSON:")
        print(response_text)
        raise ValueError("Gemini did not return valid JSON")
    
def generate_first_question(parsed_resume:ParsedResume,role_applied:str,difficulty:str):
    prompt = f"""
You are a professional technical interviewer.

Candidate Information:

Name: {parsed_resume.name}

Skills:
{parsed_resume.skills}

Projects:
{parsed_resume.projects}

Experience:
{parsed_resume.experience}

Education:
{parsed_resume.education}

Role Applied:
{role_applied}

Difficulty:
{difficulty}

Instructions:

- Ask ONLY ONE interview question.
- Make it personalized using the candidate's resume.
- Don't ask generic questions.
- Start with an introduction question or a project discussion.
- Return ONLY the question.
"""
    response=client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return response.text.strip()
    
def generate_next_question(parsed_resume:ParsedResume,role_applied:str,difficulty:str,conversation:str):
    prompt = f"""
You are an experienced technical interviewer.

Your goal is to conduct a realistic interview.

Candidate Resume

Name:
{parsed_resume.name}

Skills:
{parsed_resume.skills}

Projects:
{parsed_resume.projects}

Experience:
{parsed_resume.experience}

Education:
{parsed_resume.education}

Role Applied:
{role_applied}

Difficulty:
{difficulty}

Conversation So Far:

{conversation}

Instructions:

- Read the entire conversation carefully.
- Never repeat previous questions.
- Ask only ONE question.
- If the candidate answered well, ask a deeper follow-up.
- If the answer was weak, ask an easier clarifying question.
- Use information from the resume whenever possible.
- Behave like a real interviewer, not a scripted chatbot.
- Return ONLY the next interview question.
"""
    response=client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return response.text.strip()

