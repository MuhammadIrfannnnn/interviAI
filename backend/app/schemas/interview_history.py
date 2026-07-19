from datetime import datetime
from pydantic import BaseModel


class InterviewHistoryItem(BaseModel):
    session_id: int
    role_applied: str
    difficulty: str
    status: str
    overall_score: float
    started_at: datetime
    ended_at: datetime | None


class InterviewHistoryResponse(BaseModel):
    interviews: list[InterviewHistoryItem]