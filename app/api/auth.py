from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()


class Register(BaseModel):
    username: str
    password: str


class Login(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(reg: Register, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.username == reg.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Create user
    new_user = User(
        username=reg.username,
        password=reg.password,  # No hashing for MVP
        created_at=int(__import__('time').time())
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username}


@router.post("/login")
def login(reg: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == reg.username).first()
    if not user or user.password != reg.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Return simple token in MVP (just user ID)
    return {
        "access_token": str(user.id),
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username}
    }