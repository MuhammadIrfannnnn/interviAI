from pydantic import BaseModel
from typing import List, Literal


class CompetencyReport(BaseModel):
    competency: str
    level: Literal["Strong", "Average", "Weak"]
    summary: str


class InterviewReport(BaseModel):
    overall_score: float

    technical_score: float
    communication_score: float
    confidence_score: float
    problem_solving_score: float

    strengths: List[str]
    weaknesses: List[str]

    competency_reports: List[CompetencyReport]

    technical_evidence: List[str]

    highlights: List[str]
    concerns: List[str]

    interview_summary: str

    overall_feedback: str

    recommendation: Literal[
        "Strong Hire",
        "Hire",
        "Borderline",
        "No Hire"
    ]

    learning_roadmap: List[str]