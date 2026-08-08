from app.database.base import Base
from sqlalchemy import String, DateTime, ForeignKey,JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime


class ParsedResume(Base):
    __tablename__="parsed_resumes"
    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    resume_id:Mapped[int]=mapped_column(ForeignKey("resumes.id"),unique=True,nullable=False)
    name:Mapped[str]=mapped_column(String(100),nullable=False)
    email:Mapped[str]=mapped_column(String(255),nullable=True)
    skills:Mapped[list]=mapped_column(JSON)
    education:Mapped[list]=mapped_column(JSON)
    projects:Mapped[list]=mapped_column(JSON)
    experience:Mapped[list]=mapped_column(JSON)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    resume=relationship("Resume",back_populates="parsed_resume")
    summary: Mapped[str | None] = mapped_column(Text)
