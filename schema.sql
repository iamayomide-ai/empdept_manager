-- Employee & Department Management System — Database Schema
-- Demonstrates: Primary Keys, Foreign Keys, Constraints, Referential Integrity

DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    department_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    location        TEXT NOT NULL,
    budget          REAL NOT NULL DEFAULT 0,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    employee_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    phone           TEXT,
    position        TEXT NOT NULL,
    salary          REAL NOT NULL CHECK (salary >= 0),
    hire_date       TEXT NOT NULL,
    role_type       TEXT NOT NULL DEFAULT 'staff' CHECK (role_type IN ('staff', 'manager')),
    team_size       INTEGER,               -- only meaningful for managers
    department_id   INTEGER NOT NULL,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX idx_employees_department ON employees(department_id);

-- Seed data for demo purposes
INSERT INTO departments (name, location, budget) VALUES
    ('Information Technology', 'Block A, 2nd Floor', 5000000),
    ('Human Resources', 'Block B, Ground Floor', 2000000),
    ('Finance', 'Block A, 1st Floor', 3500000),
    ('Operations', 'Block C, Ground Floor', 2800000);

INSERT INTO employees (first_name, last_name, email, phone, position, salary, hire_date, role_type, team_size, department_id) VALUES
    ('Ada', 'Okafor', 'ada.okafor@company.com', '08012345001', 'IT Manager', 450000, '2021-03-15', 'manager', 6, 1),
    ('Emeka', 'Nwosu', 'emeka.nwosu@company.com', '08012345002', 'Systems Administrator', 280000, '2022-06-01', 'staff', NULL, 1),
    ('Ngozi', 'Bello', 'ngozi.bello@company.com', '08012345003', 'HR Manager', 400000, '2020-01-10', 'manager', 4, 2),
    ('Tunde', 'Alade', 'tunde.alade@company.com', '08012345004', 'Recruiter', 220000, '2023-02-20', 'staff', NULL, 2),
    ('Chioma', 'Eze', 'chioma.eze@company.com', '08012345005', 'Finance Manager', 480000, '2019-11-05', 'manager', 5, 3),
    ('Bayo', 'Fashola', 'bayo.fashola@company.com', '08012345006', 'Accountant', 250000, '2022-09-12', 'staff', NULL, 3);
