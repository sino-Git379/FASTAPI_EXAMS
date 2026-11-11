from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import (
    TaskAssign,
    TaskCreate,
    TaskPatch,
    TaskResponse,
    TaskStatusType,
    TaskStatusUpdate,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _validate_project_and_employee(
    db: Session, project_id: Optional[int], employee_id: Optional[int]
):
    if project_id is not None:
        project = crud.get_project(db, project_id=project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
    if employee_id is not None:
        employee = crud.get_employee(db, employee_id=employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found",
            )
        if not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign task to inactive employee",
            )


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
):
    _validate_project_and_employee(
        db, project_id=task_in.project_id, employee_id=task_in.employee_id
    )
    return crud.create_task(db, task_in=task_in)


@router.get(
    "/",
    response_model=List[TaskResponse],
    summary="Get list of tasks with filters",
)
def get_tasks(
    search: Optional[str] = Query(None, description="Search by title case-insensitively"),
    status: Optional[TaskStatusType] = Query(None, description="Filter by status (todo/in_progress/done)"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Filter by priority (1-5)"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    deadline_before: Optional[date] = Query(None, description="Tasks with deadline on or before date"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Limit for pagination (1-100)"),
    db: Session = Depends(get_db),
):
    return crud.get_tasks(
        db,
        search=search,
        status=status,
        priority=priority,
        project_id=project_id,
        employee_id=employee_id,
        deadline_before=deadline_before,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{id}",
    response_model=TaskResponse,
    summary="Get task by ID",
)
def get_task(
    id: int,
    db: Session = Depends(get_db),
):
    task = crud.get_task(db, task_id=id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.put(
    "/{id}",
    response_model=TaskResponse,
    summary="Fully update a task",
)
def update_task(
    id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = crud.get_task(db, task_id=id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    _validate_project_and_employee(
        db, project_id=task_in.project_id, employee_id=task_in.employee_id
    )

    return crud.update_task(db, db_task=task, task_in=task_in)


@router.patch(
    "/{id}",
    response_model=TaskResponse,
    summary="Partially update a task",
)
def patch_task(
    id: int,
    task_in: TaskPatch,
    db: Session = Depends(get_db),
):
    task = crud.get_task(db, task_id=id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    update_data = task_in.model_dump(exclude_unset=True)
    if not update_data:
        return task

    project_id = update_data.get("project_id")
    employee_id = update_data.get("employee_id") if "employee_id" in update_data else None

    _validate_project_and_employee(db, project_id=project_id, employee_id=employee_id)

    return crud.patch_task(db, db_task=task, update_data=update_data)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
def delete_task(
    id: int,
    db: Session = Depends(get_db),
):
    task = crud.get_task(db, task_id=id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    crud.delete_task(db, db_task=task)
    return None


@router.patch(
    "/{id}/assign",
    response_model=TaskResponse,
    summary="Assign or unassign an employee to a task",
)
def assign_task(
    id: int,
    assign_in: TaskAssign,
    db: Session = Depends(get_db),
):
    task = crud.get_task(db, task_id=id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if assign_in.employee_id is not None:
        employee = crud.get_employee(db, employee_id=assign_in.employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found",
            )
        if not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign task to inactive employee",
            )

    return crud.assign_task(db, db_task=task, employee_id=assign_in.employee_id)


@router.patch(
    "/{id}/status",
    response_model=TaskResponse,
    summary="Change status of a task",
)
def update_task_status(
    id: int,
    status_in: TaskStatusUpdate,
    db: Session = Depends(get_db),
):
    task = crud.get_task(db, task_id=id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return crud.update_task_status(db, db_task=task, status=status_in.status)
