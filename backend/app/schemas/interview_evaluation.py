from pydantic import BaseModel,Field
from typing import List

class InterviewEvaluation(BaseModel):
    technical_score:float= Field(..., ge=0, le=10)
    communication_score:float= Field(..., ge=0, le=10)
    confidence_score:float= Field(..., ge=0, le=10)
    correctness:str
    strengths:List[str]
    weaknesses:List[str]
    feedback:str
    follow_up_strategy:str