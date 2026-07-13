from pydantic import BaseModel,Field,field_validator

class InterviewAnswer(BaseModel):
    session_id:int=Field(...,gt=0)
    answer:str=Field(...,min_length=5,max_length=5000,description="candidate answer to the question")

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Answer cannot be empty.")
        return value