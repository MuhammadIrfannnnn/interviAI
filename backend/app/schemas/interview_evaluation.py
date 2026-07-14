from pydantic import BaseModel
from typing import List

class InterviewEvaluation(BaseModel):
    technical_score:int
    communication_score:int
    confidence_score:int
    correctness:str
    strengths:List[str]
    weaknesses:List[str]
    feedback:str
    follow_up_strategy:str