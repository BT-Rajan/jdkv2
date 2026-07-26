from datetime import date, datetime
from pydantic import BaseModel


class EmployeeCreateRequest(BaseModel):
    full_name: str
    designation: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    role: str | None = None


class EmployeeUpdateRequest(BaseModel):
    full_name: str | None = None
    designation: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    role: str | None = None


class EmployeeResponse(BaseModel):
    id: int
    full_name: str
    designation: str | None
    phone: str | None
    email: str | None
    address: str | None
    start_date: date | None
    end_date: date | None
    role: str | None
    created_at: datetime
    updated_at: datetime


class EmployeeListResponse(BaseModel):
    employees: list[EmployeeResponse]
    total: int
