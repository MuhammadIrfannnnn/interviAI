from app.database.base import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import String,DateTime,ForeignKey,Text
from datetime import datetime

class InterviewMessage(Base):
    __tablename__="interview_messages"

    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    session_id:Mapped[int]=mapped_column(ForeignKey("interview_sessions.id"),nullable=False)
    speaker:Mapped[str]=mapped_column(String(100))
    message:Mapped[str]=mapped_column(Text)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    session=relationship("InterviewSession",back_populates="messages")
    
    evaluation = relationship(
        "InterviewEvaluation",
        back_populates="message",
        uselist=False,
    )