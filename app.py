"""
app.py
Flask front controller — wires HTTP routes to the OOP model/repository layer.
"""

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
    total_salary = sum(e.salary for e in employees)
    manager_count = sum(1 for e in employees if e.role_type == "manager")
    return render_template(
        "dashboard.html",
        departments=departments,
        employees=employees,
        total_salary=total_salary,
        manager_count=manager_count,
    )


# ---------------------------------------------------------------------
# Department routes
# ---------------------------------------------------------------------

@app.route("/departments")
def list_departments():
    departments = dept_repo.get_all()
    counts = {d.department_id: dept_repo.employee_count(d.department_id) for d in departments}
    return render_template("departments.html", departments=departments, counts=counts)


@app.route("/departments/new", methods=["GET", "POST"])
def new_department():
    if request.method == "POST":
        d = Department(
            name=request.form["name"],
            location=request.form["location"],
            budget=float(request.form["budget"]),
        )
        dept_repo.create(d)
        flash(f"Department '{d.name}' created.", "success")
        return redirect(url_for("list_departments"))
    return render_template("department_form.html", department=None)


@app.route("/departments/<int:department_id>/edit", methods=["GET", "POST"])
def edit_department(department_id):
    d = dept_repo.get_by_id(department_id)
    if request.method == "POST":
        d.name = request.form["name"]
        d.location = request.form["location"]
        d.budget = float(request.form["budget"])
        dept_repo.update(d)
        flash(f"Department '{d.name}' updated.", "success")
        return redirect(url_for("list_departments"))
    return render_template("department_form.html", department=d)


@app.route("/departments/<int:department_id>/delete", methods=["POST"])
def delete_department(department_id):
    dept_repo.delete(department_id)
    flash("Department deleted.", "info")
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
        common_args = dict(
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            email=request.form["email"],
            phone=request.form["phone"],
            position=request.form["position"],
            salary=float(request.form["salary"]),
            hire_date=request.form["hire_date"],
            department_id=int(request.form["department_id"]),
        )
        if request.form["role_type"] == "manager":
            emp = Manager(**common_args, team_size=int(request.form.get("team_size") or 0))
        else:
            emp = Employee(**common_args)
        emp_repo.create(emp)
        flash(f"Employee '{emp.full_name}' added.", "success")
        return redirect(url_for("list_employees"))
    return render_template("employee_form.html", employee=None, departments=departments)


@app.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
def edit_employee(employee_id):
    emp = emp_repo.get_by_id(employee_id)
    departments = dept_repo.get_all()
    if request.method == "POST":
        emp._first_name = request.form["first_name"]
        emp._last_name = request.form["last_name"]
        emp.email = request.form["email"]
        emp.phone = request.form["phone"]
        emp.position = request.form["position"]
        emp.salary = float(request.form["salary"])
        emp.hire_date = request.form["hire_date"]
        emp.department_id = int(request.form["department_id"])
        emp.role_type = request.form["role_type"]
        if emp.role_type == "manager":
            emp.team_size = int(request.form.get("team_size") or 0)
        emp_repo.update(emp)
        flash(f"Employee '{emp.full_name}' updated.", "success")
        return redirect(url_for("list_employees"))
    return render_template("employee_form.html", employee=emp, departments=departments)


@app.route("/employees/<int:employee_id>/delete", methods=["POST"])
def delete_employee(employee_id):
    emp_repo.delete(employee_id)
    flash("Employee removed.", "info")
    return redirect(url_for("list_employees"))


@app.route("/employees/<int:employee_id>/raise", methods=["POST"])
def give_raise(employee_id):
    """Demonstrates calling real behaviour on an OOP object, not just editing a row."""
    emp = emp_repo.get_by_id(employee_id)
    percent = float(request.form.get("percent", 0))
    emp.give_raise(percent)
    emp_repo.update(emp)
    flash(f"{emp.full_name} given a {percent}% raise. New salary: {emp.salary:,.2f}", "success")
    return redirect(url_for("list_employees"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
