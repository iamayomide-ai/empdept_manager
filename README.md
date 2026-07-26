# Employee & Department Management System

A database-driven, object-oriented web application for managing company
departments and employees. Built with Python (Flask), SQLite, and Docker.

---

## 1. Quick Start

### Option A — Run with Docker (recommended for the defense)
```bash
# Create the DB file first so Docker mounts a file, not a folder
touch empdept.db

docker compose up --build
```
Visit **http://localhost:5000**

### Option B — Run locally without Docker
```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Visit **http://localhost:5000**

The database (`empdept.db`) and demo seed data are created automatically
the first time the app starts.

---

## 2. Project Structure
```
empdept_manager/
├── app.py              # Flask routes (Controller)
├── models.py           # OOP classes + repositories (Model)
├── database.py         # DB connection handler
├── schema.sql          # SQL schema + seed data
├── templates/           # Jinja2 HTML templates (View)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```
This follows a lightweight **MVC pattern**: `models.py` is the Model,
`templates/` is the View, `app.py` is the Controller.

---

## 3. OOP Concepts Demonstrated (for your defense)

| Concept | Where |
|---|---|
| **Abstraction** | `Person` in `models.py` is an `ABC` with an `@abstractmethod describe()` — it can never be instantiated directly. |
| **Inheritance** | `Employee(Person)` and `Manager(Employee)` — a Manager *is an* Employee *is a* Person. |
| **Encapsulation** | `email` and `salary` are private (`_email`, `_salary`) and only changed through validated `@property` setters (e.g. salary can't go negative, email must contain `@`). |
| **Polymorphism** | `describe()` behaves differently for `Employee` vs `Manager` even though both are called the same way. |
| **Factory Method** | `EmployeeRepository._row_to_object()` decides at runtime whether to build an `Employee` or a `Manager` from a database row. |
| **Repository / DAO pattern** | `DepartmentRepository` and `EmployeeRepository` isolate all raw SQL from the rest of the app — the rest of the code never writes SQL directly. |
| **Behaviour, not just data** | `Employee.give_raise(percent)` is a real method that mutates state with logic — not just a getter/setter. |

---

## 4. Database Design

Two tables, one relationship:

```
departments (1) ───< (many) employees
```

- `departments`: department_id (PK), name, location, budget
- `employees`: employee_id (PK), ..., role_type (staff/manager), department_id (FK → departments)

Referential integrity is enforced with a `FOREIGN KEY ... ON DELETE CASCADE`,
and `role_type` uses a `CHECK` constraint. See `schema.sql` for full DDL.

> Note: employees uses **single-table inheritance** — one `employees` table
> stores both `Employee` and `Manager` rows, distinguished by `role_type`.
> This is a standard technique for mapping class hierarchies to relational
> databases, and is a good talking point if asked "how did you map
> inheritance to SQL?"

---

## 5. Features
- Dashboard with live stats (headcount, managers, total payroll)
- Full CRUD for Departments and Employees
- Manager vs Staff role distinction with role-specific fields (team size)
- "Give Raise" action — demonstrates calling real OOP behavior, not just editing a field
- Input validation at the model layer (email format, non-negative salary)
- Seeded demo data so the app is populated on first run

---

## 6. Git Setup
```bash
git init
git add .
git commit -m "Initial commit: Employee & Department Management System"
```
(`.gitignore` already excludes the database file, `__pycache__`, and venv.)

---

## 7. Possible Defense Questions & Answers

**Q: Why SQLite instead of PostgreSQL/MySQL?**
A: SQLite is file-based, requires no separate server, and is ideal for a
self-contained demo. The repository pattern in `models.py` means swapping
to PostgreSQL only requires changing `database.py` — no other file touches
SQL directly.

**Q: How is this "OOP" and not just a CRUD app?**
A: The domain objects (`Employee`, `Manager`, `Department`) carry both data
*and* behavior (e.g. `give_raise()`, validated setters), and the class
hierarchy (`Person → Employee → Manager`) models a real-world "is-a"
relationship, with polymorphic `describe()`.

**Q: Why Docker?**
A: It guarantees the app runs identically on any machine (including the
panel's), without needing them to install Python or dependencies manually.
