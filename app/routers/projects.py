from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import ProjectCreate, ProjectResponse, ProjectUpdate, TaskResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
):
    if crud.get_project_by_name(db, name=project_in.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this name already exists",
        )
    return crud.create_project(db, project_in)


@router.get(
    "/",
    response_model=List[ProjectResponse],
    summary="Get list of projects",
)
def get_projects(
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=100, description="Limit for pagination"),
    db: Session = Depends(get_db),
):
    return crud.get_projects(db, offset=offset, limit=limit)


@router.get(
    "/{id}",
    response_model=ProjectResponse,
    summary="Get project by ID",
)
def get_project(
    id: int,
    db: Session = Depends(get_db),
):
    project = crud.get_project(db, project_id=id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.put(
    "/{id}",
    response_model=ProjectResponse,
    summary="Update project",
)
def update_project(
    id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = crud.get_project(db, project_id=id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    existing_named = crud.get_project_by_name(db, name=project_in.name)
    if existing_named and existing_named.id != id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this name already exists",
        )

    return crud.update_project(db, db_project=project, project_in=project_in)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
)
def delete_project(
    id: int,
    db: Session = Depends(get_db),
):
    project = crud.get_project(db, project_id=id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if crud.has_project_tasks(db, project_id=id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete project with associated tasks",
        )

    crud.delete_project(db, db_project=project)
    return None


@router.get(
    "/{id}/tasks",
    response_model=List[TaskResponse],
    summary="Get all tasks of a project",
)
def get_project_tasks(
    id: int,
    db: Session = Depends(get_db),
):
    project = crud.get_project(db, project_id=id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return crud.get_project_tasks(db, project_id=id)
