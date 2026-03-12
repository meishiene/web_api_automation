from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_subject,
    hash_password,
    verify_password,
)
from app.errors import AppException, ErrorCode
from app.services.audit_service import create_audit_log
from app.schemas.user import (
    AccessTokenResponse,
    AuthTokenResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    UserPublic,
)

router = APIRouter()


@router.post("/register", response_model=UserPublic)
def register(reg: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.username == reg.username).first()
    if existing:
        raise AppException(400, ErrorCode.USERNAME_ALREADY_EXISTS, "Username already exists")

    # Create user
    new_user = User(
        username=reg.username,
        password=hash_password(reg.password),
        created_at=int(__import__('time').time())
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    create_audit_log(
        db=db,
        request=request,
        action="auth.register",
        resource_type="user",
        resource_id=str(new_user.id),
        user_id=new_user.id,
        details={"username": new_user.username},
    )
    return new_user


@router.post("/login", response_model=AuthTokenResponse)
def login(reg: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == reg.username).first()
    if not user or not verify_password(reg.password, user.password):
        raise AppException(401, ErrorCode.INVALID_CREDENTIALS, "Invalid credentials")

    if not user.password.startswith("pbkdf2_sha256$"):
        user.password = hash_password(reg.password)
        db.commit()

    subject = str(user.id)
    access_token = create_access_token(subject)
    refresh_token = create_refresh_token(subject)
    create_audit_log(
        db=db,
        request=request,
        action="auth.login",
        resource_type="user",
        resource_id=subject,
        user_id=user.id,
        details={"username": user.username},
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "role": user.role}
    }


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh_token(payload: RefreshTokenRequest, request: Request, db: Session = Depends(get_db)):
    try:
        subject = decode_refresh_subject(payload.refresh_token)
    except ValueError as exc:
        raise AppException(401, ErrorCode.INVALID_REFRESH_TOKEN, str(exc))

    user = db.query(User).filter(User.id == int(subject)).first()
    if not user:
        raise AppException(401, ErrorCode.USER_NOT_FOUND, "User not found")

    create_audit_log(
        db=db,
        request=request,
        action="auth.refresh",
        resource_type="user",
        resource_id=subject,
        user_id=user.id,
    )

    return {
        "access_token": create_access_token(subject),
        "token_type": "bearer",
    }
