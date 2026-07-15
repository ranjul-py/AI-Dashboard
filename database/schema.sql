-- SQLite Database Schema for CEO Office Executive Dashboard

-- 1. Users Table for Role-Based Authentication
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL, -- 'CEO', 'Executive Admin', 'Viewer'
    full_name TEXT NOT NULL,
    email TEXT NOT NULL
);

-- 2. Revenue and Profit Table
CREATE TABLE IF NOT EXISTS revenue (
    month TEXT PRIMARY KEY, -- YYYY-MM
    revenue REAL NOT NULL,
    profit REAL NOT NULL
);

-- 3. Employees/Workforce Table
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    status TEXT NOT NULL, -- 'Active', 'Inactive'
    join_date TEXT NOT NULL, -- YYYY-MM-DD
    utilization_pct INTEGER NOT NULL
);

-- 4. Partners & Sales Pipeline Table
CREATE TABLE IF NOT EXISTS partners (
    partner_name TEXT PRIMARY KEY,
    pipeline_value REAL NOT NULL,
    status TEXT NOT NULL, -- 'Qualified', 'Proposal Sent', 'Negotiation', 'Won', 'Lost'
    target_pipeline REAL, -- Blended from Excel
    partner_manager TEXT,  -- Blended from Excel
    contract_date TEXT    -- Blended from Excel
);

-- 5. Projects Table
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    status TEXT NOT NULL, -- 'On Track', 'Delayed', 'At Risk'
    budget REAL NOT NULL,
    completion_pct INTEGER NOT NULL,
    delay_days INTEGER NOT NULL,
    description TEXT,     -- Blended from JSON
    client_name TEXT      -- Blended from JSON
);

-- 6. Clients Table
CREATE TABLE IF NOT EXISTS clients (
    client_name TEXT PRIMARY KEY,
    nps INTEGER NOT NULL,
    csat REAL NOT NULL,
    retention_status TEXT NOT NULL -- 'Retained', 'At Risk'
);

-- 7. API Metrics Table (e.g. for external benchmark integration)
CREATE TABLE IF NOT EXISTS api_metrics (
    metric_name TEXT PRIMARY KEY,
    metric_value REAL NOT NULL,
    last_updated TEXT NOT NULL
);

-- 8. WBR Reports Archive
CREATE TABLE IF NOT EXISTS wbr_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    generated_at TEXT NOT NULL,
    report_text TEXT NOT NULL,
    author TEXT NOT NULL
);

-- 9. Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    username TEXT NOT NULL,
    action TEXT NOT NULL,
    details TEXT NOT NULL
);
