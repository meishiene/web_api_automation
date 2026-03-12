from pydantic import BaseModel

from app.schemas.common import ORMModel


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserPublic(ORMModel):
    id: int
    username: str
    role: str


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserPublic


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str
