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


# Planner-specific schemas
class PlanOut(BaseModel):
    id: str
    name: str
    visibility: Optional[str]


class BucketOut(BaseModel):
    id: str
    title: str
    order_hint: str


class TaskOut(BaseModel):
    id: str
    title: str
    bucket_id: Optional[str]
    order_hint: str
    percent_complete: Optional[int] = 0


class CommentOut(BaseModel):
    id: str
    body: str
    created_at: Optional[str]


class MembershipOut(BaseModel):
    id: str
    user_id: str
    role: str
