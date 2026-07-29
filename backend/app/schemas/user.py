from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    full_name:str=Field(...,min_length=3,max_length=50)
    email:EmailStr
    password:str=Field(...,min_length=8)

class UserLogin(BaseModel):
    email:EmailStr
    password:str

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

class GoogleLoginRequest(BaseModel):
    id_token: str