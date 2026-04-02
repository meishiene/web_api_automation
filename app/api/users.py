from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserPublic

router = APIRouter()


@router.get("", response_model=List[UserPublic])
def list_users(
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[UserPublic]:
    return (
        db.query(User)
        .order_by(User.id.asc())
        .all()
    )
