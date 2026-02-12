from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.project import Project
from app.models.user import User
from app.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    created_at: int


@router.get("/")
def get_projects(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ProjectResponse]:
    projects = db.query(Project).filter(Project.owner_id == user.id).all()
    return projects


@router.post("/")
def create_project(
    project: ProjectCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectResponse:
    new_project = Project(
        name=project.name,
        description=project.description,
        owner_id=user.id,
        created_at=int(__import__('time').time())
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.put("/{project_id}")
def update_project(
    project_id: int,
    project: ProjectCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectResponse:
    db_project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_project.name = project.name
    db_project.description = project.description
    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted"}