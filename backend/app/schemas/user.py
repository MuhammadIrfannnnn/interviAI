from pydantic import BaseModel, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    full_name:str=Field(...,min_length=3,max_length=50)
    email:EmailStr
    password:str=Field(...,min_length=8)

    @field_validator("full_name")
    @classmethod
    def _trim_full_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Full name cannot be empty.")
        return trimmed

class UserLogin(BaseModel):
    email:EmailStr
    password:str=Field(...,min_length=1)

class UserResponse(BaseModel):
    id:int
    email:EmailStr
    full_name:str
    role:str
    model_config = {
        "from_attributes": True
    }

class TokenResponse(BaseModel):
    access_token:str
    token_type:str

class RegisterResponse(BaseModel):
    message: str
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

    @field_validator("otp")
    @classmethod
    def _otp_digits_only(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("OTP must contain only digits.")
        return value


class ResendOtpRequest(BaseModel):
    email: EmailStr


class MessageResponse(BaseModel):
    message: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)

    @field_validator("otp")
    @classmethod
    def _otp_digits_only(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("OTP must contain only digits.")
        return value

class GoogleLoginRequest(BaseModel):
    id_token: str