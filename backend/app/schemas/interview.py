from pydantic import BaseModel,Field
from typing import Literal
class InterviewStart(BaseModel):
    role_applied:str=Field(...,min_length=2,max_length=100,description="Job role candidate is applying for")
    difficulty:Literal["Easy","Medium","Hard"]