from datetime import datetime
from sqlalchemy import String,DateTime
from sqlalchemy.orm import Mapped, mapped_column,relationship
from app.database.base import Base
from enum import Enum
from sqlalchemy import Enum as SqlEnum


class AuthProvider(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"

class UserRole(str, Enum):
    CANDIDATE = "candidate"
    ADMIN = "admin"

class OtpPurpose(str, Enum):
    VERIFY_EMAIL = "verify_email"
    RESET_PASSWORD = "reset_password"

class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name:Mapped[str] = mapped_column(String(50),nullable=False)
    email:Mapped[str]=mapped_column(String(255),unique=True,nullable=False,index=True)
    hashed_password:Mapped[str]=mapped_column(String(255),nullable=False)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole),default=UserRole.CANDIDATE)
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resume=relationship("Resume", back_populates="user", uselist=False)
    interview_sessions=relationship("InterviewSession",back_populates="user")
    is_verified: Mapped[bool] = mapped_column(default=False)
    auth_provider: Mapped[AuthProvider] = mapped_column(SqlEnum(AuthProvider),default=AuthProvider.LOCAL)
    otp_hash: Mapped[str | None] = mapped_column(String(255),nullable=True)
    otp_purpose: Mapped[OtpPurpose | None] = mapped_column(SqlEnum(OtpPurpose),nullable=True)
    otp_expires_at: Mapped[datetime | None] = mapped_column(DateTime,nullable=True,)
    last_otp_sent_at: Mapped[datetime | None] = mapped_column(DateTime,nullable=True,)