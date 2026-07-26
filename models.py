"""
models.py
Core OOP layer of the system.

Demonstrates:
  - Abstraction   -> Person is an abstract base class (ABC)
  - Inheritance   -> Employee and Manager both derive from Person
  - Encapsulation -> private attributes with validation via properties
  - Polymorphism  -> describe() behaves differently per subclass
"""

from abc import ABC, abstractmethod
from database import Database


# ---------------------------------------------------------------------
# Abstraction + Inheritance + Encapsulation + Polymorphism
# ---------------------------------------------------------------------

class Person(ABC):
    """Abstract base class — cannot be instantiated directly."""

    def __init__(self, first_name, last_name, email):
        self._first_name = first_name
        self._last_name = last_name
        self.email = email  # goes through the property setter below

    @property
    def full_name(self):
        return f"{self._first_name} {self._last_name}"

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        # Encapsulation: validate before allowing the attribute to be set
        if "@" not in value:
            raise ValueError(f"Invalid email address: {value}")
        self._email = value

    @abstractmethod
    def describe(self):
        """Every subclass must define how it describes itself (polymorphism)."""
        raise NotImplementedError


class Employee(Person):
    """A regular staff member belonging to a department."""

    def __init__(self, first_name, last_name, email, phone, position,
                 salary, hire_date, department_id, employee_id=None):
        super().__init__(first_name, last_name, email)
        self.phone = phone
        self.position = position
        self._salary = salary
        self.hire_date = hire_date
        self.department_id = department_id
        self.employee_id = employee_id
        self.role_type = "staff"

    @property
    def salary(self):
        return self._salary

    @salary.setter
    def salary(self, value):
        if value < 0:
            raise ValueError("Salary cannot be negative")
        self._salary = value

    def give_raise(self, percent):
        """Behaviour beyond simple data storage — real OOP, not just a struct."""
        self._salary += self._salary * (percent / 100)
        return self._salary

    def describe(self):
        return f"{self.full_name} — {self.position} (Staff)"


class Manager(Employee):
    """A Manager IS an Employee (inheritance) with extra responsibility."""

    def __init__(self, first_name, last_name, email, phone, position,
                 salary, hire_date, department_id, team_size=0, employee_id=None):
        super().__init__(first_name, last_name, email, phone, position,
                          salary, hire_date, department_id, employee_id)
        self.team_size = team_size
        self.role_type = "manager"

    def describe(self):
        # Polymorphism: overrides Employee.describe()
        return f"{self.full_name} — {self.position} (Manages {self.team_size} staff)"


class Department:
    """A department that groups employees together."""

    def __init__(self, name, location, budget, department_id=None):
        self.name = name
        self.location = location
        self.budget = budget
        self.department_id = department_id

    def __repr__(self):
        return f"<Department {self.name}>"


# ---------------------------------------------------------------------
# Repository layer — encapsulates all SQL for each entity (DAO pattern)
# ---------------------------------------------------------------------

class DepartmentRepository:
    def __init__(self):
        self.db = Database()

    def get_all(self):
        rows = self.db.fetch_all("SELECT * FROM departments ORDER BY name")
        return [Department(r["name"], r["location"], r["budget"], r["department_id"]) for r in rows]

    def get_by_id(self, department_id):
        r = self.db.fetch_one("SELECT * FROM departments WHERE department_id = ?", (department_id,))
        return Department(r["name"], r["location"], r["budget"], r["department_id"]) if r else None

    def create(self, department: Department):
        return self.db.execute(
            "INSERT INTO departments (name, location, budget) VALUES (?, ?, ?)",
            (department.name, department.location, department.budget),
        )

    def update(self, department: Department):
        self.db.execute(
            "UPDATE departments SET name=?, location=?, budget=? WHERE department_id=?",
            (department.name, department.location, department.budget, department.department_id),
        )

    def delete(self, department_id):
        self.db.execute("DELETE FROM departments WHERE department_id = ?", (department_id,))

    def employee_count(self, department_id):
        r = self.db.fetch_one(
            "SELECT COUNT(*) as cnt FROM employees WHERE department_id = ?", (department_id,)
        )
        return r["cnt"] if r else 0


class EmployeeRepository:
    def __init__(self):
        self.db = Database()

    def _row_to_object(self, r):
        """Factory method: builds an Employee or Manager depending on role_type
        (Factory pattern + polymorphism)."""
        if r["role_type"] == "manager":
            return Manager(r["first_name"], r["last_name"], r["email"], r["phone"],
                            r["position"], r["salary"], r["hire_date"], r["department_id"],
                            team_size=r["team_size"] or 0, employee_id=r["employee_id"])
        return Employee(r["first_name"], r["last_name"], r["email"], r["phone"],
                         r["position"], r["salary"], r["hire_date"], r["department_id"],
                         employee_id=r["employee_id"])

    def get_all(self):
        rows = self.db.fetch_all("""
            SELECT e.*, d.name as department_name FROM employees e
            JOIN departments d ON e.department_id = d.department_id
            ORDER BY e.last_name
        """)
        results = []
        for r in rows:
            obj = self._row_to_object(r)
            obj.department_name = r["department_name"]
            results.append(obj)
        return results

    def get_by_id(self, employee_id):
        r = self.db.fetch_one("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
        return self._row_to_object(r) if r else None

    def get_by_department(self, department_id):
        rows = self.db.fetch_all(
            "SELECT * FROM employees WHERE department_id = ? ORDER BY last_name", (department_id,)
        )
        return [self._row_to_object(r) for r in rows]

    def create(self, employee):
        return self.db.execute(
            """INSERT INTO employees
               (first_name, last_name, email, phone, position, salary, hire_date,
                role_type, team_size, department_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (employee._first_name, employee._last_name, employee.email, employee.phone,
             employee.position, employee.salary, employee.hire_date, employee.role_type,
             getattr(employee, "team_size", None), employee.department_id),
        )

    def update(self, employee):
        self.db.execute(
            """UPDATE employees SET first_name=?, last_name=?, email=?, phone=?, position=?,
               salary=?, hire_date=?, role_type=?, team_size=?, department_id=?
               WHERE employee_id=?""",
            (employee._first_name, employee._last_name, employee.email, employee.phone,
             employee.position, employee.salary, employee.hire_date, employee.role_type,
             getattr(employee, "team_size", None), employee.department_id, employee.employee_id),
        )

    def delete(self, employee_id):
        self.db.execute("DELETE FROM employees WHERE employee_id = ?", (employee_id,))
