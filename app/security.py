import base64
import hashlib
import hmac
import os
import time
from typing import Any, Dict

from jose import JWTError, jwt

from app.config import settings

PASSWORD_SCHEME = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        settings.PASSWORD_HASH_ITERATIONS,
    )
    salt_b64 = base64.urlsafe_b64encode(salt).decode("utf-8")
    digest_b64 = base64.urlsafe_b64encode(digest).decode("utf-8")
    return f"{PASSWORD_SCHEME}${settings.PASSWORD_HASH_ITERATIONS}${salt_b64}${digest_b64}"


def _verify_pbkdf2_password(plain_password: str, stored_password: str) -> bool:
    parts = stored_password.split("$")
    if len(parts) != 4:
        return False

    _, iterations_raw, salt_b64, digest_b64 = parts
    try:
        iterations = int(iterations_raw)
        salt = base64.urlsafe_b64decode(salt_b64.encode("utf-8"))
        expected_digest = base64.urlsafe_b64decode(digest_b64.encode("utf-8"))
    except (ValueError, TypeError):
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(actual_digest, expected_digest)


def verify_password(plain_password: str, stored_password: str) -> bool:
    if stored_password.startswith(f"{PASSWORD_SCHEME}$"):
        return _verify_pbkdf2_password(plain_password, stored_password)
    return hmac.compare_digest(plain_password, stored_password)


def _create_token(subject: str, token_type: str, expires_in_minutes: int) -> str:
    now = int(time.time())
    payload: Dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_in_minutes * 60,
        "jti": base64.urlsafe_b64encode(os.urandom(8)).decode("utf-8"),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str) -> str:
    return _create_token(subject, "access", settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(subject: str) -> str:
    return _create_token(subject, "refresh", settings.REFRESH_TOKEN_EXPIRE_MINUTES)


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def decode_refresh_subject(token: str) -> str:
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    if payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    subject = payload.get("sub")
    if subject is None:
        raise ValueError("Invalid token subject")
    return str(subject)
