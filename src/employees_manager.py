"""
employees_manager.py
~~~~~~~~~~~~~~~~~~~~
CRUD‑style helper around an `employees` table, using SQLAlchemy Core/ORM.

Prerequisites
-------------
pip install sqlalchemy psycopg2‑binary

Make sure db_connection.py (with `engine`, `SessionLocal`) is importable.
"""

from contextlib import contextmanager
from typing import Any, Dict, List, Sequence

from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.db_connection import engine, SessionLocal

Base = declarative_base()


class Employee(Base):
    """ORM model mirroring the DB table"""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    job_history = Column(String)
    salary = Column(Numeric(precision=12, scale=2), nullable=False)
    years_of_experience = Column(Integer, nullable=False)

    # Optional: nice Pythonic representation
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Employee(id={self.id}, name='{self.name}', title='{self.title}', "
            f"salary={float(self.salary):,.2f}, yoe={self.years_of_experience})>"
        )


# Ensure the table exists (safe to run repeatedly)
Base.metadata.create_all(bind=engine)


@contextmanager
def _session_scope():
    """Provide a transactional scope around a series of operations."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class EmployeesManager:
    """
    High‑level helper class wrapping common operations on the employees table.
    Usage:
        mgr = EmployeesManager()
        mgr.create_employee(...)
        top = mgr.get_top_employees(3, order_by=["-salary", "name"])
    """

    # ---------- Read ----------
    def get_top_employees(
        self,
        n: int = 5,
        order_by: Sequence[str] | None = None,
        filters: Dict[str, Any] | None = None,
    ) -> List[Employee]:
        """
        Return **n** employees ordered by the specified columns.

        Parameters
        ----------
        n : int
            Maximum number of rows to return.
        order_by : list[str] | None
            Columns to sort by.  Use a leading '-' for descending, e.g. "-salary".
            Defaults to ["-salary"].
        filters : dict[str, Any] | None
            Exact‑match filters, e.g. {"title": "Data Analyst"}.

        Example
        -------
        mgr.get_top_employees(10,
                              order_by=["-years_of_experience", "name"],
                              filters={"title": "Software Engineer"})
        """
        order_by = order_by or ["-salary"]
        filters = filters or {}

        with _session_scope() as session:
            query = session.query(Employee)

            # exact‑match filtering
            for attr, value in filters.items():
                query = query.filter(getattr(Employee, attr) == value)

            # build ORDER BY clause
            ordering_clauses = []
            for key in order_by:
                desc = key.startswith("-")
                col_name = key[1:] if desc else key
                col = getattr(Employee, col_name)
                ordering_clauses.append(col.desc() if desc else col.asc())

            return query.order_by(*ordering_clauses).limit(n).all()

    # ---------- Create ----------
    def create_employee(
        self,
        name: str,
        title: str,
        job_history: str,
        salary: float,
        years_of_experience: int,
    ) -> Employee:
        with _session_scope() as session:
            emp = Employee(
                name=name,
                title=title,
                job_history=job_history,
                salary=salary,
                years_of_experience=years_of_experience,
            )
            session.add(emp)
            session.flush()  # populate emp.id
            return emp

    # ---------- Update ----------
    def update_employee(self, emp_id: int, **updates) -> Employee:
        with _session_scope() as session:
            try:
                emp: Employee = (
                    session.query(Employee)
                    .filter(Employee.id == emp_id)
                    .one()
                )
            except NoResultFound:
                raise ValueError(f"Employee with id {emp_id} does not exist")

            for attr, value in updates.items():
                if hasattr(emp, attr):
                    setattr(emp, attr, value)
            session.add(emp)
            return emp

    # ---------- Delete ----------
    def delete_employee(self, emp_id: int) -> None:
        with _session_scope() as session:
            deleted = session.query(Employee).filter(Employee.id == emp_id).delete()
            if not deleted:
                raise ValueError(f"Employee with id {emp_id} does not exist")

