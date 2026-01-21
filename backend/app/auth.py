from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import schemas, models, utils
import os
from .database import get_db
from .emailer import send_email
from .rate_limiter import check_ip, check_key

security = HTTPBearer()

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup", response_model=schemas.MessageResponse)
def signup(payload: schemas.SignUpRequest, request: Request, db: Session = Depends(get_db)):
    # basic IP rate-limit
    if not check_ip(request):
        raise HTTPException(status_code=429, detail="Too many requests")
    # basic rate limiting by email and IP
    # note: request not available here; callers should check IP limiter externally if needed
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    pwd_hash = utils.hash_password(payload.password)
    user = models.User(email=payload.email, password_hash=pwd_hash)
    db.add(user)
    db.commit()
    db.refresh(user)

    # create verification token
    token = utils.random_token()
    token_hash = utils.hash_token(token)
    otp = models.OneTimeToken(user_id=user.id, token_hash=token_hash, type=models.TokenType.email_verification, expires_at=datetime.utcnow()+timedelta(minutes=30))
    db.add(otp)
    db.commit()

    frontend = os.getenv('FRONTEND_URL', 'http://localhost:9005')
    link = f"{frontend}/verify-email?token={token}"
    sent = send_email(user.email, "Verify your email", f"Click to verify: {link}")
    if not sent:
        print(f"[DEV] Verification link: {link}")
    return {"detail": "Sign-up successful. Check email for verification link."}


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> models.User:
    token = credentials.credentials
    try:
        payload = utils.decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    uid = payload.get("sub")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.id == uid).first()
    if not user or user.status.name == 'deleted':
        raise HTTPException(status_code=401, detail="User not found")
    if user.status.name == 'suspended':
        raise HTTPException(status_code=403, detail="Account suspended")
    return user

@router.post("/signin", response_model=schemas.TokenResponse)
def signin(payload: schemas.SignInRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    # basic IP rate-limit
    if not check_ip(request):
        raise HTTPException(status_code=429, detail="Too many requests")
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or user.status.name == 'deleted':
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if user.status.name == 'suspended':
        raise HTTPException(status_code=403, detail="Account suspended")
    if not user.password_hash or not utils.verify_password(user.password_hash, payload.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.email_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    access_token = utils.create_access_token(user.id, expires_minutes=15)
    refresh_plain = utils.random_token()
    refresh_hash = utils.hash_token(refresh_plain)
    expires_at = datetime.utcnow() + timedelta(days=14)
    rt = models.RefreshToken(user_id=user.id, token_hash=refresh_hash, expires_at=expires_at)
    db.add(rt)
    db.commit()

    # set refresh token cookie and CSRF double-submit cookie
    secure_flag = os.getenv("ENV", "production") == "production"
    csrf = utils.random_token(16)
    response.set_cookie("refresh_token", refresh_plain, httponly=True, secure=secure_flag, samesite='lax', max_age=14*24*3600)
    response.set_cookie("csrf_token", csrf, httponly=False, secure=secure_flag, samesite='lax', max_age=14*24*3600)
    return {"access_token": access_token}

@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    # CSRF double-submit check
    csrf_header = request.headers.get("x-csrf")
    csrf_cookie = request.cookies.get("csrf_token")
    if not csrf_header or not csrf_cookie or csrf_header != csrf_cookie:
        raise HTTPException(status_code=403, detail="CSRF token missing or invalid")

    cookie = request.cookies.get("refresh_token")
    if not cookie:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    h = utils.hash_token(cookie)
    rt = db.query(models.RefreshToken).filter(models.RefreshToken.token_hash == h).first()
    if not rt or rt.revoked or rt.expires_at < datetime.utcnow():
        # Token reuse detection could go here
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    # rotate refresh token
    new_plain = utils.random_token()
    new_hash = utils.hash_token(new_plain)
    rt.revoked = True
    db.add(models.RefreshToken(user_id=rt.user_id, token_hash=new_hash, expires_at=datetime.utcnow()+timedelta(days=14)))
    db.commit()
    secure_flag = os.getenv("ENV", "production") == "production"
    csrf = utils.random_token(16)
    response.set_cookie("refresh_token", new_plain, httponly=True, secure=secure_flag, samesite='lax', max_age=14*24*3600)
    response.set_cookie("csrf_token", csrf, httponly=False, secure=secure_flag, samesite='lax', max_age=14*24*3600)
    access_token = utils.create_access_token(rt.user_id, expires_minutes=15)
    return {"access_token": access_token}

@router.post("/logout", response_model=schemas.MessageResponse)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    csrf_header = request.headers.get("x-csrf")
    csrf_cookie = request.cookies.get("csrf_token")
    if not csrf_header or not csrf_cookie or csrf_header != csrf_cookie:
        raise HTTPException(status_code=403, detail="CSRF token missing or invalid")

    cookie = request.cookies.get("refresh_token")
    if cookie:
        h = utils.hash_token(cookie)
        rt = db.query(models.RefreshToken).filter(models.RefreshToken.token_hash == h).first()
        if rt:
            rt.revoked = True
            db.commit()
    response.delete_cookie("refresh_token")
    response.delete_cookie("csrf_token")
    return {"detail": "Logged out"}

@router.post("/verify-email", response_model=schemas.MessageResponse)
def verify_email(payload: schemas.VerifyRequest, db: Session = Depends(get_db)):
    h = utils.hash_token(payload.token)
    otp = db.query(models.OneTimeToken).filter(models.OneTimeToken.token_hash == h, models.OneTimeToken.type==models.TokenType.email_verification).first()
    if not otp or otp.used or otp.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.id == otp.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    user.email_verified = True
    otp.used = True
    db.commit()
    return {"detail": "Email verified"}

@router.post("/forgot-password", response_model=schemas.MessageResponse)
def forgot_password(payload: schemas.ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    if not check_ip(request):
        raise HTTPException(status_code=429, detail="Too many requests")
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if user:
        token = utils.random_token()
        h = utils.hash_token(token)
        otp = models.OneTimeToken(user_id=user.id, token_hash=h, type=models.TokenType.password_reset, expires_at=datetime.utcnow()+timedelta(hours=1))
        db.add(otp)
        db.commit()
        frontend = os.getenv('FRONTEND_URL', 'http://localhost:9005')
        print(f"[DEV] Password reset link: {frontend}/reset-password?token={token}")
    # Always return success to avoid enumeration
    return {"detail": "If that email exists, a reset link was sent."}

@router.post("/reset-password", response_model=schemas.MessageResponse)
def reset_password(payload: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    h = utils.hash_token(payload.token)
    otp = db.query(models.OneTimeToken).filter(models.OneTimeToken.token_hash == h, models.OneTimeToken.type==models.TokenType.password_reset).first()
    if not otp or otp.used or otp.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.id == otp.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    user.password_hash = utils.hash_password(payload.new_password)
    otp.used = True
    # Revoke refresh tokens
    rts = db.query(models.RefreshToken).filter(models.RefreshToken.user_id == user.id).all()
    for r in rts:
        r.revoked = True
    db.commit()
    return {"detail": "Password has been reset"}


@router.get("/sessions", response_model=List[schemas.SessionInfo])
def list_sessions(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    rts = db.query(models.RefreshToken).filter(models.RefreshToken.user_id == current_user.id).all()
    out = []
    for r in rts:
        out.append(schemas.SessionInfo(id=r.id, device_info=r.device_info, expires_at=r.expires_at.isoformat() if r.expires_at else None, revoked=bool(r.revoked), created_at=r.created_at.isoformat() if r.created_at else None))
    return out


@router.post("/sessions/revoke", response_model=schemas.MessageResponse)
def revoke_session(req: schemas.RevokeSessionRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    rt = db.query(models.RefreshToken).filter(models.RefreshToken.id == req.session_id, models.RefreshToken.user_id == current_user.id).first()
    if not rt:
        raise HTTPException(status_code=404, detail="Session not found")
    rt.revoked = True
    db.commit()
    return {"detail": "Session revoked"}


@router.post("/sessions/revoke-all", response_model=schemas.MessageResponse)
def revoke_all_sessions(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    rts = db.query(models.RefreshToken).filter(models.RefreshToken.user_id == current_user.id, models.RefreshToken.revoked == False).all()
    for r in rts:
        r.revoked = True
    db.commit()
    return {"detail": "All sessions revoked"}


@router.post("/trial", response_model=schemas.TokenResponse)
def trial_access(payload: schemas.TrialRequest, request: Request, db: Session = Depends(get_db)):
    if not check_ip(request):
        raise HTTPException(status_code=429, detail="Too many requests")
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    # allow trial only within 1 day of creation
    if user.created_at + timedelta(days=1) < datetime.utcnow():
        raise HTTPException(status_code=403, detail="Trial expired; please verify your email")
    access_token = utils.create_access_token(user.id, expires_minutes=24 * 60, extra_claims={"trial": True})
    return {"access_token": access_token}
