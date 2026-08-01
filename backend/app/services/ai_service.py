from app.schemas.resume import ParsedResume
from google import genai
from app.core.config import settings
from app.schemas.interview_evaluation import InterviewEvaluation
from app.schemas.interview_decision import InterviewDecision
from app.schemas.interview_plan import InterviewPlan
from app.schemas.interview_state import InterviewState
import json
from app.schemas.interview_report import InterviewReport

client=genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL="gemini-3.5-flash"

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
    
def generate_first_question(resume_summary:str,role_applied:str,difficulty:str):
    prompt = f"""
You are a professional technical interviewer.

Candidate Information:

resume Summary:
{resume_summary}

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
    
def generate_next_question(resume_summary:str,role_applied:str,difficulty:str,conversation:str,plan:InterviewPlan):
    prompt = f"""
You are an experienced interviewer.

IMPORTANT:

The interview planning has ALREADY been completed.

You MUST follow the planner's decision.

Do NOT decide what competency to assess next.

Do NOT change topics unless instructed by the planner.

Your ONLY responsibility is writing the next interview question.

------------------------------------------------------------
CANDIDATE INFORMATION
------------------------------------------------------------

resume Summary:
{resume_summary}

Role Applied:
{role_applied}

Difficulty:
{difficulty}

------------------------------------------------------------
PLANNER DECISION
------------------------------------------------------------

{plan.model_dump_json(indent=2)}

------------------------------------------------------------
INTERVIEW CONVERSATION
------------------------------------------------------------

{conversation}

------------------------------------------------------------
QUESTION WRITING RULES
------------------------------------------------------------

1. Ask EXACTLY ONE interview question.

2. Follow the planner decision exactly.

3. Follow the planner guidance.

4. Never ignore the planner.

5. If the planner selected "continue_topic",
ask a meaningful follow-up that explores the topic further.

6. If the planner selected "switch_topic",
transition naturally before asking the next question.

7. If the planner selected "increase_difficulty",
make the next question noticeably more challenging.

8. If the planner selected "decrease_difficulty",
simplify the next question without sounding patronizing.

9. Do NOT ask multiple questions.

10. Do NOT repeat previous questions.

11. Sound like an experienced human interviewer.

12. The interview should feel conversational rather than scripted.

13. If changing competency, use a smooth transition such as:

"Let's switch gears slightly..."

or

"I'd like to move to another area..."

14. Use the candidate's resume whenever appropriate to personalize the question.

15. Avoid long questions.

16. Do NOT explain your reasoning.

17. Return ONLY the interview question.

No markdown.

No code fences.

No explanations.

Return ONLY the question.
"""
    response=client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return response.text.strip()

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
        return InterviewDecision(**data)

    except json.JSONDecodeError:
        print(response_text)
        raise ValueError("Gemini did not return valid JSON")
    

def plan_next_step(resume_summary:str,role_applied:str,difficulty:str,conversation:str,evaluations:str,state:InterviewState):
    prompt = f"""
You are an expert senior hiring manager responsible for PLANNING an interview.

IMPORTANT:
You are NOT the interviewer.
You NEVER ask interview questions.
You NEVER answer interview questions.

Your ONLY responsibility is deciding what the interviewer should do next.

------------------------------------------------------------
CANDIDATE INFORMATION
------------------------------------------------------------

resume Summary: 
{resume_summary}

Role Applied:
{role_applied}

Difficulty:
{difficulty}

------------------------------------------------------------
INTERVIEW CONVERSATION
------------------------------------------------------------

{conversation}

------------------------------------------------------------
EVALUATION HISTORY
------------------------------------------------------------

{evaluations}

------------------------------------------------------------
CURRENT INTERVIEW STATE
------------------------------------------------------------

{state.model_dump_json(indent=2)}

------------------------------------------------------------
YOUR OBJECTIVE
------------------------------------------------------------

Plan the remainder of the interview exactly as an experienced human interviewer would.

Your goal is NOT to test only technical knowledge.

Your goal is to collect enough evidence to evaluate the candidate across multiple dimensions before deciding whether to hire them.

------------------------------------------------------------
COMPETENCIES TO ASSESS
------------------------------------------------------------

Assess as many of these as appropriate for the candidate level.

- Introduction
- Resume Discussion
- Projects
- Technical Knowledge
- Problem Solving
- System Design (only if appropriate)
- Behavioral
- Communication
- Teamwork
- Leadership
- Motivation
- Career Goals

------------------------------------------------------------
PLANNING RULES
------------------------------------------------------------

1. Use Interview State as the PRIMARY source of truth.

2. Use Conversation only for additional context.

3. Use Evaluation History to understand strengths and weaknesses.

4. Prefer discussing projects, experience and skills that actually exist in the candidate's resume.

5. Never repeatedly ask about the same topic if it has already been sufficiently assessed.

6. Normally ask at most 2-3 questions for a competency.

7. If the candidate demonstrates STRONG understanding of a competency,
move to another competency.

8. If the candidate struggles after multiple attempts,
stop insisting and move to another competency.

9. Avoid making the interview feel repetitive.

10. Mix technical and non-technical questions naturally.

11. Ask behavioral questions naturally instead of treating them as a separate section.

12. Only include System Design questions when the candidate level and role justify them.

13. Adapt the interview according to:
- Resume
- Candidate performance
- Difficulty
- Role

14. The interview should feel conversational, not like a scripted checklist.

15. It is acceptable to revisit a previous competency later if new evidence is needed.

16. End the interview ONLY after enough evidence has been collected across multiple competencies.

17. Never end the interview after evaluating only one area.

18. If the interview is already well balanced and sufficient evidence exists, choose "end_interview".

------------------------------------------------------------
AVAILABLE ACTIONS
------------------------------------------------------------

continue_topic
switch_topic
increase_difficulty
decrease_difficulty
end_interview

------------------------------------------------------------
AVAILABLE COMPETENCIES
------------------------------------------------------------

Introduction

Resume

Projects

Technical

Problem Solving

System Design

Behavioral

Communication

Teamwork

Leadership

Motivation

Career Goals

------------------------------------------------------------
OUTPUT FORMAT
------------------------------------------------------------

Return ONLY valid JSON matching the InterviewPlan schema.

Example:

{{
    "action": "switch_topic",
    "next_competency": "Behavioral",
    "topic": "Conflict Resolution",
    "reason": "Technical competency has been sufficiently assessed and behavioral evidence is still missing.",
    "guidance": "Ask a situational behavioral question about resolving disagreements within a team.",
    "transition": "Let's move away from technical implementation and talk about teamwork."
}}

Do NOT return markdown.

Do NOT return explanations.

Do NOT return code fences.

Return ONLY the JSON object.
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
        return InterviewPlan(**data)

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

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    print("Gemini Response")
    print(response.text)
    print("------------------------------------------------------------")

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    response_text = response.text.strip()

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