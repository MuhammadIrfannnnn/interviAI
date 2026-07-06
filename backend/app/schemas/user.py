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
