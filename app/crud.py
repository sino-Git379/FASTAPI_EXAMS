from datetime import date
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Employee, Project, Task
from app.schemas import (
    EmployeeCreate,
    EmployeeUpdate,
    ProjectCreate,
    ProjectUpdate,
    TaskCreate,
    TaskUpdate,
)


def get_project(db: Session, project_id: int):
    stmt = select(Project).where(Project.id == project_id)
    return db.scalars(stmt).first()


def get_project_by_name(db: Session, name: str):
    stmt = select(Project).where(Project.name == name)
    return db.scalars(stmt).first()


def get_projects(db: Session, offset: int = 0, limit: int = 100):
    stmt = select(Project).order_by(Project.id.asc()).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


def create_project(db: Session, project_in: ProjectCreate):
    db_project = Project(
        name=project_in.name,
        description=project_in.description,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project(db: Session, db_project: Project, project_in: ProjectUpdate):
    db_project.name = project_in.name
    db_project.description = project_in.description
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, db_project: Project):
    db.delete(db_project)
    db.commit()


def get_project_tasks(db: Session, project_id: int):
    stmt = select(Task).where(Task.project_id == project_id).order_by(Task.id.asc())
    return list(db.scalars(stmt).all())


def has_project_tasks(db: Session, project_id: int):
    stmt = select(func.count(Task.id)).where(Task.project_id == project_id)
    count = db.scalar(stmt) or 0
    return count > 0


def get_employee(db: Session, employee_id: int):
    stmt = select(Employee).where(Employee.id == employee_id)
    return db.scalars(stmt).first()


def get_employee_by_email(db: Session, email: str):
    stmt = select(Employee).where(Employee.email == email)
    return db.scalars(stmt).first()


def get_employees(
    db: Session,
    search: Optional[str] = None,
    position: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
):
    stmt = select(Employee)
    if search:
        stmt = stmt.where(Employee.full_name.ilike(f"%{search}%"))
    if position:
        stmt = stmt.where(Employee.position.ilike(f"%{position}%"))
    stmt = stmt.order_by(Employee.id.asc()).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


def create_employee(db: Session, employee_in: EmployeeCreate):
    db_employee = Employee(
        full_name=employee_in.full_name,
        email=employee_in.email,
        position=employee_in.position,
        is_active=employee_in.is_active,
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(db: Session, db_employee: Employee, employee_in: EmployeeUpdate):
    db_employee.full_name = employee_in.full_name
    db_employee.email = employee_in.email
    db_employee.position = employee_in.position
    db_employee.is_active = employee_in.is_active
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, db_employee: Employee):
    db.delete(db_employee)
    db.commit()


def get_employee_tasks(db: Session, employee_id: int):
    stmt = select(Task).where(Task.employee_id == employee_id).order_by(Task.id.asc())
    return list(db.scalars(stmt).all())


def has_employee_tasks(db: Session, employee_id: int):
    stmt = select(func.count(Task.id)).where(Task.employee_id == employee_id)
    count = db.scalar(stmt) or 0
    return count > 0


def get_task(db: Session, task_id: int):
    stmt = select(Task).where(Task.id == task_id)
    return db.scalars(stmt).first()


def get_tasks(
    db: Session,
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    project_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    deadline_before: Optional[date] = None,
    offset: int = 0,
    limit: int = 100,
):
    stmt = select(Task)
    if search:
        stmt = stmt.where(Task.title.ilike(f"%{search}%"))
    if status:
        stmt = stmt.where(Task.status == status)
    if priority is not None:
        stmt = stmt.where(Task.priority == priority)
    if project_id is not None:
        stmt = stmt.where(Task.project_id == project_id)
    if employee_id is not None:
        stmt = stmt.where(Task.employee_id == employee_id)
    if deadline_before is not None:
        stmt = stmt.where(Task.deadline <= deadline_before)
    stmt = stmt.order_by(Task.id.asc()).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


def create_task(db: Session, task_in: TaskCreate):
    db_task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        deadline=task_in.deadline,
        project_id=task_in.project_id,
        employee_id=task_in.employee_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, db_task: Task, task_in: TaskUpdate):
    db_task.title = task_in.title
    db_task.description = task_in.description
    db_task.status = task_in.status
    db_task.priority = task_in.priority
    db_task.deadline = task_in.deadline
    db_task.project_id = task_in.project_id
    db_task.employee_id = task_in.employee_id
    db.commit()
    db.refresh(db_task)
    return db_task


def patch_task(db: Session, db_task: Task, update_data: Dict[str, Any]):
    for key, value in update_data.items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, db_task: Task):
    db.delete(db_task)
    db.commit()


def assign_task(db: Session, db_task: Task, employee_id: Optional[int]):
    db_task.employee_id = employee_id
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task_status(db: Session, db_task: Task, status: str):
    db_task.status = status
    db.commit()
    db.refresh(db_task)
    return db_task
