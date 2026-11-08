"""
app.py
Flask front controller — wires HTTP routes to the OOP model/repository layer.
"""

import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db
from models import Department, Employee, Manager, DepartmentRepository, EmployeeRepository

app = Flask(__name__)
app.secret_key = "siwes-defense-secret-key"  # fine for a demo project

dept_repo = DepartmentRepository()
emp_repo = EmployeeRepository()


@app.route("/")
def dashboard():
    departments = dept_repo.get_all()
    employees = emp_repo.get_all()
    # Pushed aggregations to the DBMS instead of in-memory Python calculations
    stats = emp_repo.get_dashboard_stats()
    return render_template(
        "dashboard.html",
        departments=departments,
        employees=employees,
        total_salary=stats["total_payroll"],
        manager_count=stats["manager_count"],
    )


# ---------------------------------------------------------------------
# Department routes
# ---------------------------------------------------------------------

@app.route("/departments")
def list_departments():
    # Single SQL query with LEFT JOIN + GROUP BY eliminates N+1 queries
    departments, counts = dept_repo.get_all_with_counts()
    return render_template("departments.html", departments=departments, counts=counts)


@app.route("/departments/new", methods=["GET", "POST"])
def new_department():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            location = request.form.get("location", "").strip()
            budget = float(request.form.get("budget", 0))
            if not name or not location:
                flash("Department name and location are required.", "danger")
                return render_template("department_form.html", department=None)
            d = Department(name=name, location=location, budget=budget)
            dept_repo.create(d)
            flash(f"Department '{d.name}' created successfully.", "success")
            return redirect(url_for("list_departments"))
        except sqlite3.IntegrityError:
            flash("A department with this name already exists (UNIQUE constraint violated).", "danger")
        except ValueError as e:
            flash(f"Invalid input: {e}", "danger")
        except Exception as e:
            flash(f"Database error: {e}", "danger")
    return render_template("department_form.html", department=None)


@app.route("/departments/<int:department_id>/edit", methods=["GET", "POST"])
def edit_department(department_id):
    d = dept_repo.get_by_id(department_id)
    if not d:
        flash("Department not found.", "danger")
        return redirect(url_for("list_departments"))
    if request.method == "POST":
        try:
            d.name = request.form.get("name", "").strip()
            d.location = request.form.get("location", "").strip()
            d.budget = float(request.form.get("budget", 0))
            if not d.name or not d.location:
                flash("Department name and location are required.", "danger")
                return render_template("department_form.html", department=d)
            dept_repo.update(d)
            flash(f"Department '{d.name}' updated.", "success")
            return redirect(url_for("list_departments"))
        except sqlite3.IntegrityError:
            flash("A department with this name already exists (UNIQUE constraint violated).", "danger")
        except ValueError as e:
            flash(f"Invalid input: {e}", "danger")
        except Exception as e:
            flash(f"Database error: {e}", "danger")
    return render_template("department_form.html", department=d)


@app.route("/departments/<int:department_id>/delete", methods=["POST"])
def delete_department(department_id):
    try:
        dept_repo.delete(department_id)
        flash("Department deleted (associated employees removed via ON DELETE CASCADE).", "info")
    except Exception as e:
        flash(f"Database error deleting department: {e}", "danger")
    return redirect(url_for("list_departments"))


# ---------------------------------------------------------------------
# Employee routes
# ---------------------------------------------------------------------

@app.route("/employees")
def list_employees():
    employees = emp_repo.get_all()
    return render_template("employees.html", employees=employees)


@app.route("/employees/new", methods=["GET", "POST"])
def new_employee():
    departments = dept_repo.get_all()
    if request.method == "POST":
        try:
            common_args = dict(
                first_name=request.form.get("first_name", "").strip(),
                last_name=request.form.get("last_name", "").strip(),
                email=request.form.get("email", "").strip(),
                phone=request.form.get("phone", "").strip(),
                position=request.form.get("position", "").strip(),
                salary=float(request.form.get("salary", 0)),
                hire_date=request.form.get("hire_date", "").strip(),
                department_id=int(request.form.get("department_id", 0)),
            )
            if request.form.get("role_type") == "manager":
                emp = Manager(**common_args, team_size=int(request.form.get("team_size") or 0))
            else:
                emp = Employee(**common_args)
            emp_repo.create(emp)
            flash(f"Employee '{emp.full_name}' added successfully.", "success")
            return redirect(url_for("list_employees"))
        except sqlite3.IntegrityError:
            flash("An employee with this email already exists (UNIQUE constraint violated).", "danger")
        except ValueError as e:
            flash(f"Validation error: {e}", "danger")
        except Exception as e:
            flash(f"Database error: {e}", "danger")
    return render_template("employee_form.html", employee=None, departments=departments)


@app.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
def edit_employee(employee_id):
    emp = emp_repo.get_by_id(employee_id)
    if not emp:
        flash("Employee not found.", "danger")
        return redirect(url_for("list_employees"))
    departments = dept_repo.get_all()
    if request.method == "POST":
        try:
            emp._first_name = request.form.get("first_name", "").strip()
            emp._last_name = request.form.get("last_name", "").strip()
            emp.email = request.form.get("email", "").strip()
            emp.phone = request.form.get("phone", "").strip()
            emp.position = request.form.get("position", "").strip()
            emp.salary = float(request.form.get("salary", 0))
            emp.hire_date = request.form.get("hire_date", "").strip()
            emp.department_id = int(request.form.get("department_id", 0))
            emp.role_type = request.form.get("role_type", "staff")
            if emp.role_type == "manager":
                emp.team_size = int(request.form.get("team_size") or 0)
            emp_repo.update(emp)
            flash(f"Employee '{emp.full_name}' updated successfully.", "success")
            return redirect(url_for("list_employees"))
        except sqlite3.IntegrityError:
            flash("An employee with this email already exists (UNIQUE constraint violated).", "danger")
        except ValueError as e:
            flash(f"Validation error: {e}", "danger")
        except Exception as e:
            flash(f"Database error: {e}", "danger")
    return render_template("employee_form.html", employee=emp, departments=departments)


@app.route("/employees/<int:employee_id>/delete", methods=["POST"])
def delete_employee(employee_id):
    try:
        emp_repo.delete(employee_id)
        flash("Employee removed successfully.", "info")
    except Exception as e:
        flash(f"Database error removing employee: {e}", "danger")
    return redirect(url_for("list_employees"))


@app.route("/employees/<int:employee_id>/raise", methods=["POST"])
def give_raise(employee_id):
    """Demonstrates calling real behaviour on an OOP object, persisted to the database."""
    emp = emp_repo.get_by_id(employee_id)
    if not emp:
        flash("Employee not found.", "danger")
        return redirect(url_for("list_employees"))
    try:
        percent = float(request.form.get("percent", 0))
        emp.give_raise(percent)
        emp_repo.update(emp)
        flash(f"{emp.full_name} given a {percent}% raise. New salary: ₦{emp.salary:,.2f}", "success")
    except ValueError as e:
        flash(f"Salary update failed: {e}", "danger")
    except Exception as e:
        flash(f"Error applying raise: {e}", "danger")
    return redirect(url_for("list_employees"))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5050))
    print(f"\n * Employee Dashboard is running at http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=True)
