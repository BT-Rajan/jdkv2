from fastapi import APIRouter, Depends, Query

from app.core.sentinel_access import AuthenticatedIdentity
from app.core.security import require_permission
from app.domain.employees.service import EmployeeService
from app.permissions.definitions import EMPLOYEES_VIEW, EMPLOYEES_MANAGE
from app.models.employees import (
    EmployeeCreateRequest, EmployeeUpdateRequest, EmployeeResponse, EmployeeListResponse,
)

router = APIRouter(prefix="/api/employees", tags=["employees"])

_service = EmployeeService()


@router.get("", response_model=EmployeeListResponse)
def search_employees(
    q: str | None = Query(None),
    role: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    identity: AuthenticatedIdentity = Depends(require_permission(EMPLOYEES_VIEW)),
):
    rows, total = _service.search(q, role, limit, offset)
    return EmployeeListResponse(employees=[EmployeeResponse(**r) for r in rows], total=total)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, identity: AuthenticatedIdentity = Depends(require_permission(EMPLOYEES_VIEW))):
    return EmployeeResponse(**_service.get(employee_id))


@router.post("", response_model=EmployeeResponse)
def create_employee(body: EmployeeCreateRequest, identity: AuthenticatedIdentity = Depends(require_permission(EMPLOYEES_MANAGE))):
    return EmployeeResponse(**_service.create(identity, body.model_dump()))


@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, body: EmployeeUpdateRequest,
                     identity: AuthenticatedIdentity = Depends(require_permission(EMPLOYEES_MANAGE))):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    return EmployeeResponse(**_service.update(identity, employee_id, data))


@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: int, identity: AuthenticatedIdentity = Depends(require_permission(EMPLOYEES_MANAGE))):
    _service.delete(identity, employee_id)
