import json
import logging
import time

from google import genai
from google.genai import types
import httpx

from app.core.config import settings
from app.schemas.interview_decision import InterviewDecision
from app.schemas.interview_evaluation import InterviewEvaluation
from app.schemas.interview_plan import InterviewPlan
from app.schemas.interview_report import InterviewReport
from app.schemas.interview_state import InterviewState
from app.schemas.resume import ParsedResume
from app.schemas.interview_turn import InterviewTurn

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL = "gemini-3.6-flash"


def _compact_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)


class GeminiServiceUnavailable(RuntimeError):
    """Raised when Gemini is temporarily unavailable after retries."""

    def __init__(self, message: str = "The AI interviewer is temporarily unavailable. Please try again in a moment."):
        super().__init__(message)
        self.message = message


def _is_retryable_error(error: Exception) -> bool:
    if isinstance(error, (TimeoutError, httpx.TimeoutException)):
        return True

    status_code = getattr(error, "code", None)
    if isinstance(status_code, int) and status_code in {429, 500, 502, 503, 504}:
        return True

    status_text = str(getattr(error, "status", "") or "").lower()
    error_text = str(error).lower()
    if status_text in {"429", "500", "502", "503", "504"}:
        return True
    if "high demand" in error_text or "service unavailable" in error_text:
        return True

    return False


def generate_with_retry(prompt: str, *, model: str = MODEL) -> str:
    last_error: Exception | None = None

    logger.info("MODEL: %s", model)
    logger.info("PROMPT LENGTH: %s", len(prompt))
    logger.info("PROMPT PREVIEW: %s", prompt[:400].replace("\n", " "))

    for attempt in range(1, 4):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            response_text = getattr(response, "text", None)
            if not response_text:
                raise ValueError("Gemini returned an empty response")
            return response_text.strip()
        except Exception as error:
            logger.warning("Gemini request failed (attempt %s/3): %s", attempt, error)
            last_error = error

            should_retry = attempt < 3 and (
                _is_retryable_error(error)
                or "empty response" in str(error).lower()
            )
            if should_retry:
                delay = 2 ** attempt
                logger.warning(
                    "Retrying Gemini request (attempt %s/3)...",
                    attempt + 1,
                )
                time.sleep(delay)
                continue

            break

    raise GeminiServiceUnavailable("The AI interviewer is temporarily unavailable. Please try again in a moment.") from last_error

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
    response_text = generate_with_retry(prompt)
    response_text = response_text.strip()
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
    
def generate_first_question(candidate_name: str,role_applied:str,difficulty:str):
    prompt = f"""You are interviewing {candidate_name} for {role_applied} (difficulty: {difficulty}).

Output ONLY a short human-sounding greeting + ONE intro question asking the candidate to briefly introduce themselves and relate their background/interests to the role. No project or technical questions, no markdown, no extra text.

Example:
"Hi Muhammad, great to have you here. To start, could you briefly introduce yourself and tell me what interested you in this Data Analyst Intern role?\""""

    return generate_with_retry(prompt)

def generate_interview_turn(
    resume_summary: str,
    role_applied: str,
    difficulty: str,
    conversation: str,
    state: InterviewState,
) -> InterviewTurn:

    prompt = f"""
You are handling one interview turn.

First evaluate the latest candidate answer.

Then decide the next action:
- continue_topic
- switch_topic
- increase_difficulty
- decrease_difficulty
- end_interview

Then update the interview state.

Then write exactly ONE next interview question.

Return ONLY valid JSON in this exact format:

{{
  "evaluation": "short evaluation",
  "action": "continue_topic",
  "updated_state": {{ ... }},
  "next_question": "question"
}}

Resume Summary:
{resume_summary}

Role:
{role_applied}

Difficulty:
{difficulty}

Conversation:
{conversation}

Current Interview State:
{_compact_json(state.model_dump())}

For every competency level, you MUST use ONLY one of these values(case-sensitive):

- Not Assessed
- Weak
- Average
- Strong


Rules:
- Evaluate only the latest candidate answer.
- Keep evaluation under 40 words.
- Use the interview state as the source of truth.
- Update only the competency discussed.
- Do NOT invent new competencies.
- Ask exactly one question.
- Return ONLY valid JSON.
"""

    response_text = generate_with_retry(prompt).strip()

    if response_text.startswith("```json"):
        response_text = response_text.replace("```json", "", 1)

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    try:
        data = json.loads(response_text)
        return InterviewTurn(**data)

    except json.JSONDecodeError:
        print(response_text)
        raise ValueError("Gemini did not return valid JSON")

def evaluate_answer(resume_summary:str,role_applied:str,difficulty:str,conversation:str,candidate_answer:str):
    prompt = f"""
You are a senior technical interviewer.

Evaluate ONLY the candidate's MOST RECENT answer.

Candidate Resume

resume Summary:
{resume_summary}
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
    response_text = generate_with_retry(prompt)
    response_text = response_text.strip()
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
    
def should_end_interview(parsed_resume:ParsedResume,role_applied:str,difficulty:str,conversation:str,evaluations:str):
    prompt = f"""
You are an experienced technical interviewer.

Candidate Resume

Skills:
{parsed_resume.skills}

Projects:
{parsed_resume.projects}

Experience:
{parsed_resume.experience}

Role Applied:
{role_applied}

Difficulty:
{difficulty}

Interview Conversation

{conversation}

Evaluations

{evaluations}

Your job is to decide whether the interview should continue.

Guidelines

- End the interview if enough technical depth has been explored.
- End if approximately 6-10 meaningful questions have already been asked.
- Continue if important topics remain unexplored.
- Continue if candidate performance is still unclear.
- Avoid repeating questions.

Return ONLY valid JSON.

Do NOT include markdown.

Do NOT include triple backticks.

{{
    "end_interview": bool (True/False),
    "reason": str (Candidate demonstrated sufficient technical depth.)
}}
"""
    response_text = generate_with_retry(prompt)
    response_text = response_text.strip()
    if response_text.startswith("```json"):
        response_text=response_text.replace("```json","",1)
    if response_text.endswith("```"):
        response_text=response_text[:-3]
    response_text=response_text.strip()
    try:
        data = json.loads(response_text)
        return InterviewDecision(**data)

    except json.JSONDecodeError:
        print(response_text)
        raise ValueError("Gemini did not return valid JSON")
    


    
def update_interview_state(state:InterviewState,evaluation:str,conversation:str)->InterviewState:
    prompt=f"""
You are responsible for maintaining the interview state.

You are NOT the interviewer.

Current Interview State:

{state.model_dump_json(indent=2)}

Latest Evaluation:

{evaluation}

Conversation:

{conversation}

Update ONLY the interview state.

Rules:

- Increase attempts for the competency discussed.
- Update level:
    - Strong
    - Average
    - Weak
- Mark covered=True once assessed.
- Update last_topic.
- Do NOT invent new competencies.
- Keep unrelated competencies unchanged.

Return ONLY valid JSON matching the InterviewState schema.
"""
    response_text = generate_with_retry(prompt)
    response_text = response_text.strip()
    if response_text.startswith("```json"):
        response_text=response_text.replace("```json","",1)
    if response_text.endswith("```"):
        response_text=response_text[:-3]
    response_text=response_text.strip()
    try:
        data = json.loads(response_text)
        return InterviewState(**data)

    except json.JSONDecodeError:
        print(response_text)
        raise ValueError("Gemini did not return valid JSON")
    
def generate_final_report(
    resume_summary: str,
    role_applied: str,
    difficulty: str,
    conversation: str,
    evaluations: str,
    state: InterviewState,
):
    prompt = f"""
You are a Senior Engineering Hiring Manager.

The interview has now concluded.

Your task is NOT to ask another question.

Your task is to produce the FINAL interview assessment.

=========================================================
CANDIDATE INFORMATION
=========================================================

resume Summary: 
{resume_summary}

=========================================================
INTERVIEW DETAILS
=========================================================

Role Applied:
{role_applied}

Difficulty:
{difficulty}

=========================================================
FULL INTERVIEW CONVERSATION
=========================================================

{conversation}

=========================================================
ANSWER EVALUATIONS
=========================================================

{evaluations}

=========================================================
FINAL INTERVIEW STATE
=========================================================

{state.model_dump_json(indent=2)}

=========================================================
YOUR RESPONSIBILITIES
=========================================================

Evaluate the candidate based on the ENTIRE interview.

Do NOT judge only the last answer.

Use the resume, conversation, evaluations and interview state together.

Think like a real senior engineering hiring manager.

Your evaluation should be balanced, evidence-based and realistic.

=========================================================
SCORING
=========================================================

Provide scores between 0 and 10 for:

- technical_score
- communication_score
- confidence_score
- problem_solving_score

Then calculate:

overall_score

The overall score should reflect the complete interview,
not simply the average.

=========================================================
STRENGTHS
=========================================================

List 3-6 genuine strengths demonstrated during the interview.

Avoid repeating similar ideas.

=========================================================
WEAKNESSES
=========================================================

List genuine weaknesses observed.

They should be constructive and actionable.

=========================================================
COMPETENCY REPORTS
=========================================================

For every competency that was assessed, provide:

- competency
- level
    (Strong, Average, Weak)
- summary

Use the Interview State as the primary source of truth.

=========================================================
TECHNICAL EVIDENCE
=========================================================

List concrete technical evidence observed during the interview.

Examples:

- Explained adversarial attacks.
- Discussed SIMD optimization.
- Optimized memory access.
- Compared latency vs accuracy.
- Explained HTTPS authentication.

Only include evidence actually discussed.

=========================================================
HIGHLIGHTS
=========================================================

List the most impressive moments of the interview.

=========================================================
CONCERNS
=========================================================

List any concerns a hiring manager should know before making a decision.

=========================================================
OVERALL FEEDBACK
=========================================================

Write a professional summary of approximately 5-8 sentences.

Discuss:

- Technical depth
- Communication
- Confidence
- Problem solving
- Behavioral performance
- Overall readiness for the role

=========================================================
HIRING RECOMMENDATION
=========================================================
Return the field EXACTLY as:

"recommendation": ""
Choose EXACTLY ONE:

- Strong Hire
- Hire
- Borderline
- No Hire

Base this on the complete interview.

=========================================================
LEARNING ROADMAP
=========================================================

Provide 3-6 concrete recommendations that would genuinely help the candidate improve.

Avoid generic advice like:

"Practice more."

Instead write recommendations specific to the interview.

=========================================================
IMPORTANT
=========================================================

Return ONLY valid JSON matching the InterviewReport schema.

Do NOT include markdown.

Do NOT include explanations.

Do NOT include triple backticks.

Return ONLY valid JSON.
"""

    response_text = generate_with_retry(prompt)
    response_text = response_text.strip()

    if response_text.startswith("```json"):
        response_text = response_text.replace("```json", "", 1)

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    try:
        data = json.loads(response_text)
        print(json.dumps(data, indent=4))
        return InterviewReport(**data)

    except json.JSONDecodeError:
        print(response_text)
        raise ValueError("Gemini did not return valid JSON.")