from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User


def get_current_user(
    x_user_id: int = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.id == x_user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user