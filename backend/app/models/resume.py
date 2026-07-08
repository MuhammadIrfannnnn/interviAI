from datetime import datetime
from app.database.base import Base
from sqlalchemy import String, DateTime, ForeignKey,Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Resume(Base):
    __tablename__="resumes"

    id:Mapped[int]=mapped_column(primary_key=True, index=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"), nullable=False,unique=True)
    file_name:Mapped[str]=mapped_column(String(255))
    file_path:Mapped[str]=mapped_column(String(500))
    extracted_text:Mapped[str]=mapped_column(Text)
    uploaded_at:Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    user=relationship("User", back_populates="resume")


