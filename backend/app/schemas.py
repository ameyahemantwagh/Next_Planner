from pydantic import BaseModel, EmailStr
from typing import Optional

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MessageResponse(BaseModel):
    detail: str

class VerifyRequest(BaseModel):
    token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class SessionInfo(BaseModel):
    id: str
    device_info: Optional[str]
    expires_at: Optional[str]
    revoked: bool
    created_at: Optional[str]

class RevokeSessionRequest(BaseModel):
    session_id: str

class TrialRequest(BaseModel):
    email: EmailStr
