from datetime import datetime, date
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

TaskStatusType = Literal["todo", "in_progress", "done"]


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150, description="Project name")
    description: Optional[str] = Field(None, description="Project description")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=150, description="Full name")
    email: EmailStr = Field(..., max_length=150, description="Work email")
    position: Optional[str] = Field(None, max_length=100, description="Job position")
    is_active: bool = Field(True, description="Active status")


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: TaskStatusType = Field("todo", description="Task status")
    priority: int = Field(..., ge=1, le=5, description="Priority from 1 to 5")
    deadline: Optional[date] = Field(None, description="Task deadline date")
    project_id: int = Field(..., description="Project ID")
    employee_id: Optional[int] = Field(None, description="Assigned Employee ID")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskPatch(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatusType] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    deadline: Optional[date] = None
    project_id: Optional[int] = None
    employee_id: Optional[int] = None


class TaskAssign(BaseModel):
    employee_id: Optional[int] = Field(None, description="Employee ID to assign, or null to unassign")


class TaskStatusUpdate(BaseModel):
    status: TaskStatusType = Field(..., description="New task status")


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: int
    deadline: Optional[date]
    created_at: datetime
    project_id: int
    employee_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)
