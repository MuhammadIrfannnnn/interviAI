from pydantic import BaseModel
from typing import Literal

class CompetencyState(BaseModel):
    covered: bool = False

    level: Literal[
        "Not Assessed",
        "Weak",
        "Average",
        "Strong"
    ] = "Not Assessed"

    attempts: int = 0
    last_topic:str=""
    reason:str=""

class InterviewState(BaseModel):

    introduction: CompetencyState = CompetencyState()

    resume: CompetencyState = CompetencyState()

    projects: CompetencyState = CompetencyState()

    technical: CompetencyState = CompetencyState()

    problem_solving: CompetencyState = CompetencyState()

    behavioral: CompetencyState = CompetencyState()

    communication: CompetencyState = CompetencyState()

    teamwork: CompetencyState = CompetencyState()

    leadership: CompetencyState = CompetencyState()

    motivation: CompetencyState = CompetencyState()

    career_goals: CompetencyState = CompetencyState()