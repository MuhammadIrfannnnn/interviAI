from datetime import datetime
from sqlalchemy import String,DateTime
from sqlalchemy.orm import Mapped, mapped_column,relationship
from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name:Mapped[str] = mapped_column(String(50),nullable=False)
    email:Mapped[str]=mapped_column(String(255),unique=True,nullable=False,index=True)
    hashed_password:Mapped[str]=mapped_column(String(255),nullable=False)
    role:Mapped[str]=mapped_column(String(50),default="candidate")
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resume=relationship("Resume", back_populates="user", uselist=False)