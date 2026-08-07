from typing import Literal

from pydantic import BaseModel

from app.schemas.interview_state import InterviewState


class InterviewTurn(BaseModel):
    evaluation: str
    action: Literal[
        "continue_topic",
        "switch_topic",
        "increase_difficulty",
        "decrease_difficulty",
        "end_interview",
    ] = "continue_topic"
    updated_state: InterviewState
    next_question: str
