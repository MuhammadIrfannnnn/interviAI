from pydantic import BaseModel


class InterviewDecision(BaseModel):
    end_interview:bool
    reason:str
