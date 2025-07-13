from typing import List, Optional, Dict

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, ConfigDict

from src.employees_manager import EmployeesManager


router = APIRouter(prefix="/employees", tags=["Employees"])
manager = EmployeesManager()


# --- Pydantic Schemas ---
class EmployeeCreate(BaseModel):
    name: str
    title: str
    job_history: Optional[str] = None
    salary: float = Field(..., ge=0)
    years_of_experience: int = Field(..., ge=0)


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    job_history: Optional[str] = None
    salary: Optional[float] = Field(None, ge=0)
    years_of_experience: Optional[int] = Field(None, ge=0)

    def dict_updates(self) -> Dict:
        return {k: v for k, v in self.model_dump().items() if v is not None}


class EmployeeOut(BaseModel):
    id: int
    name: str
    title: str
    job_history: Optional[str]
    salary: float
    years_of_experience: int

    model_config = ConfigDict(from_attributes=True)


# --- Endpoints ---
@router.get(
    "",
    response_model=List[EmployeeOut],
    summary="List / search employees",
)
def list_employees(
    top: int = Query(10, gt=0),
    order_by: List[str] = Query(["-salary"]),
    title: Optional[str] = Query(None),
):
    filters = {"title": title} if title else {}
    emps = manager.get_top_employees(n=top, order_by=order_by, filters=filters)
    return emps


@router.post(
    "",
    response_model=EmployeeOut,
    status_code=201,
    summary="Create a new employee",
)
def create_employee(payload: EmployeeCreate):
    emp = manager.create_employee(**payload.model_dump())
    return emp


@router.put(
    "/{emp_id}",
    response_model=EmployeeOut,
    summary="Update an existing employee",
)
def update_employee(emp_id: int, payload: EmployeeUpdate):
    updates = payload.dict_updates()
    if not updates:
        raise HTTPException(400, "No fields provided to update")

    try:
        emp = manager.update_employee(emp_id, **updates)
    except ValueError as exc:
        raise HTTPException(404, str(exc))
    return emp


@router.delete(
    "/{emp_id}",
    status_code=204,
    summary="Delete an employee",
)
def delete_employee(emp_id: int):
    try:
        manager.delete_employee(emp_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc))
