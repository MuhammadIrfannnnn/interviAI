from app.database.base import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import String,DateTime,ForeignKey,Float,Column
from datetime import datetime
from sqlalchemy import JSON

class InterviewSession(Base):
    __tablename__="interview_sessions"

    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),nullable=False)
    resume_id:Mapped[int]=mapped_column(ForeignKey("resumes.id"),nullable=False)
    role_applied:Mapped[str]=mapped_column(String(100),nullable=False)
    difficulty:Mapped[str]=mapped_column(String(20),default="Medium")
    status:Mapped[str]=mapped_column(String(20),default="Started")
    started_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    ended_at:Mapped[datetime]=mapped_column(DateTime,nullable=True)
    overall_score:Mapped[float]=mapped_column(Float,default=0)
    user=relationship("User",back_populates="interview_sessions")
    resume=relationship("Resume",back_populates="interview_sessions")
    messages=relationship("InterviewMessage",back_populates="session",cascade="all, delete-orphan")
    interview_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    report = relationship(
        "InterviewReport",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )