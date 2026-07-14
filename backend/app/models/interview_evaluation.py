from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)

    message_id: Mapped[int] = mapped_column(
        ForeignKey("interview_messages.id"),
        unique=True,
    )

    technical_score: Mapped[int] = mapped_column(Integer)

    communication_score: Mapped[int] = mapped_column(Integer)

    confidence_score: Mapped[int] = mapped_column(Integer)

    correctness: Mapped[str] = mapped_column(Text)

    strengths: Mapped[list] = mapped_column(JSON)

    weaknesses: Mapped[list] = mapped_column(JSON)

    feedback: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    message = relationship(
        "InterviewMessage",
        back_populates="evaluation",
    )