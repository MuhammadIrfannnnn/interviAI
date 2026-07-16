from pydantic import BaseModel
from typing import Literal

class InterviewPlan(BaseModel):
    action: Literal[
        "continue_topic",
        "switch_topic",
        "increase_difficulty",
        "decrease_difficulty",
        "end_interview"
    ]
    next_competency: Literal[
        "Introduction",
        "Resume",
        "Projects",
        "Technical",
        "Problem Solving",
        "System Design",
        "Behavioral",
        "Communication",
        "Teamwork",
        "Leadership",
        "Motivation",
        "Career Goals"
    ]
    topic: str
    reason: str
    guidance: str
    transition: str