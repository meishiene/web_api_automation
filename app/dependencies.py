from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from typing import Callable
from app.database import get_db
from app.models.user import User
from app.permissions import Permission, has_permission
from app.security import decode_token
from app.errors import AppException, ErrorCode

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    if not token:
        raise AppException(401, ErrorCode.NOT_AUTHENTICATED, "Not authenticated")

    try:
        payload = decode_token(token)
    except JWTError:
        raise AppException(401, ErrorCode.INVALID_TOKEN, "Invalid token")

    if payload.get("type") != "access":
        raise AppException(401, ErrorCode.INVALID_TOKEN_TYPE, "Invalid token type")

    subject = payload.get("sub")
    if subject is None:
        raise AppException(401, ErrorCode.INVALID_TOKEN_SUBJECT, "Invalid token subject")

    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise AppException(401, ErrorCode.INVALID_TOKEN_SUBJECT, "Invalid token subject")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise AppException(401, ErrorCode.USER_NOT_FOUND, "User not found")
    return user


def require_roles(*roles: str) -> Callable[[User], User]:
    allowed_roles = {role.strip().lower() for role in roles if role and role.strip()}

    def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
        return user

    return _checker


def require_permissions(*permissions: Permission | str) -> Callable[[User], User]:
    required_permissions = [permission for permission in permissions]

    def _checker(user: User = Depends(get_current_user)) -> User:
        if not required_permissions:
            return user

        if not any(has_permission(user.role, permission) for permission in required_permissions):
            raise AppException(403, ErrorCode.FORBIDDEN, "Forbidden")
        return user

    return _checker
