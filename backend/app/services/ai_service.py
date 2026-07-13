from app.schemas.resume import ParsedResume
from google import genai
from app.core.config import settings
from app.schemas.interview_evaluation import InterviewEvaluation
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
    
def generate_next_question(parsed_resume:ParsedResume,role_applied:str,difficulty:str,conversation:str,evaluation:InterviewEvaluation):
    prompt = f"""
You are a senior technical interviewer.

Candidate Resume

Name:
{parsed_resume.name}

Skills:
{parsed_resume.skills}

Projects:
{parsed_resume.projects}

Conversation

{conversation}

Latest Evaluation

Technical Score:
{evaluation.technical_score}

Communication Score:
{evaluation.communication_score}

Confidence Score:
{evaluation.confidence_score}

Correctness:
{evaluation.correctness}

Strengths:
{evaluation.strengths}

Weaknesses:
{evaluation.weaknesses}

Follow-up Strategy:
{evaluation.follow_up_strategy}

Role:
{role_applied}

Difficulty:
{difficulty}

Instructions

- Ask ONLY ONE question.
- Adapt based on the evaluation.
- If the answer lacked depth, ask a deeper follow-up.
- If the answer was incorrect, guide the candidate toward the concept.
- If the answer was excellent, increase difficulty.
- Never repeat previous questions.
- Return ONLY the next interview question.
"""
    response=client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return response.text.strip()

def evaluate_answer(parsed_resume:ParsedResume,role_applied:str,difficulty:str,conversation:str,candidate_answer:str):
    prompt = f"""
You are a senior technical interviewer.

Evaluate ONLY the candidate's MOST RECENT answer.

Candidate Resume

Name:
{parsed_resume.name}

Skills:
{parsed_resume.skills}

Projects:
{parsed_resume.projects}

Experience:
{parsed_resume.experience}

Conversation So Far:

{conversation}

Latest Candidate Answer:

{candidate_answer}

Role:
{role_applied}

Difficulty:
{difficulty}

Return ONLY valid JSON.

Do NOT include markdown.

Do NOT include triple backticks.

Return:

{{
    "technical_score": integer from 0-10,
    "communication_score": integer from 0-10,
    "confidence_score": integer from 0-10,
    "correctness":"Correct / Partially Correct / Incorrect",
    "strengths":[...],
    "weaknesses":[...],
    "feedback":"short paragraph",
    "follow_up_strategy":"What should interviewer ask next"
}}
Scoring Guidelines:

Technical Score (0-10)

0-2 = Completely wrong

3-4 = Very weak understanding

5-6 = Basic understanding

7-8 = Good technical explanation

9-10 = Expert-level explanation

Communication Score

Evaluate clarity, organization and explanation.

Confidence Score

Estimate confidence based ONLY on the wording of the answer.
Do NOT assume confidence from resume.
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
        return InterviewEvaluation(**data)

    except json.JSONDecodeError:
        print(response_text)
        raise ValueError("Gemini did not return valid JSON")
    
