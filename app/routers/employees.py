from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate, TaskResponse

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee",
)
def create_employee(
    employee_in: EmployeeCreate,
    db: Session = Depends(get_db),
):
    if crud.get_employee_by_email(db, email=employee_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this email already exists",
        )
    return crud.create_employee(db, employee_in=employee_in)


@router.get(
    "/",
    response_model=List[EmployeeResponse],
    summary="Get list of employees",
)
def get_employees(
    search: Optional[str] = Query(None, description="Search by full_name case-insensitively"),
    position: Optional[str] = Query(None, description="Filter by position"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=100, description="Limit for pagination"),
    db: Session = Depends(get_db),
):
    return crud.get_employees(
        db,
        search=search,
        position=position,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{id}",
    response_model=EmployeeResponse,
    summary="Get employee by ID",
)
def get_employee(
    id: int,
    db: Session = Depends(get_db),
):
    employee = crud.get_employee(db, employee_id=id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    return employee


@router.put(
    "/{id}",
    response_model=EmployeeResponse,
    summary="Update employee",
)
def update_employee(
    id: int,
    employee_in: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    employee = crud.get_employee(db, employee_id=id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    existing_email = crud.get_employee_by_email(db, email=employee_in.email)
    if existing_email and existing_email.id != id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this email already exists",
        )

    return crud.update_employee(db, db_employee=employee, employee_in=employee_in)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete employee",
)
def delete_employee(
    id: int,
    db: Session = Depends(get_db),
):
    employee = crud.get_employee(db, employee_id=id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    if crud.has_employee_tasks(db, employee_id=id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete employee with assigned tasks",
        )

    crud.delete_employee(db, db_employee=employee)
    return None


@router.get(
    "/{id}/tasks",
    response_model=List[TaskResponse],
    summary="Get all tasks assigned to an employee",
)
def get_employee_tasks(
    id: int,
    db: Session = Depends(get_db),
):
    employee = crud.get_employee(db, employee_id=id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    return crud.get_employee_tasks(db, employee_id=id)
