# ⚡ TaskLink – Freelance Micro-Task Platform

A full-stack DBMS mini-project built with **Python Flask**, **MySQL**, and **Bootstrap 5**.

---

## 📋 Project Overview

TaskLink is a simplified Fiverr/Upwork-like platform that connects:
- **Clients** – Post tasks and hire freelancers
- **Freelancers** – Browse tasks, apply, submit work, and get paid
- **Admin** – Monitor all users, tasks, payments, and logs

---

## ✨ Features

| Feature | Details |
|---|---|
| Role-based login | Admin / Client / Freelancer |
| Task Management | Post, assign, submit, approve, cancel |
| Applications | Freelancers apply with bid + proposal |
| Payments | Released after approval with workload multiplier |
| Notifications | DB-driven, deadline alerts 1 hr before due |
| Reviews | 1–5 star rating after task completion |
| Monthly Reports | Auto-updated on payment release |
| Activity Logs | Tracks every major action |
| Admin Panel | Full control over users and tasks |

---

## 🚀 Setup Instructions

### Step 1 – Clone / Extract the Project

```
cd tasklink
```

### Step 2 – Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 3 – Set up MySQL

Open **MySQL Workbench** and run:

```sql
-- Either run the schema file:
SOURCE /path/to/tasklink/schema.sql;

-- OR just create the database (Flask will create tables):
CREATE DATABASE tasklink_db CHARACTER SET utf8mb4;
```

### Step 4 – Configure Database Credentials

Open `config.py` and update:

```python
MYSQL_USER     = "root"        # your MySQL username
MYSQL_PASSWORD = "root"        # your MySQL password
MYSQL_HOST     = "localhost"
MYSQL_DB       = "tasklink_db"
```

### Step 5 – Seed Sample Data

```bash
python seed_data.py
```

### Step 6 – Run the Application

```bash
python app.py
```

Open your browser: **http://127.0.0.1:5000**

---

## 🔑 Sample Login Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@gmail.com | admin123 |
| Client | client@gmail.com | client123 |
| Freelancer | freelancer@gmail.com | free123 |

---

## 🗄️ Database Schema

11 tables: `users`, `categories`, `tasks`, `applications`, `assignments`,
`submissions`, `payments`, `reviews`, `notifications`, `activity_logs`, `monthly_reports`

**DBMS Concepts Covered:**
- Primary & Foreign Keys
- Normalization (1NF, 2NF, 3NF)
- Indexing on frequently queried columns
- Stored Procedure (`GetFreelancerSummary`)
- Trigger (`after_task_completed`)
- Transactions (payment release flow)
- Role-based access control

---

## 🧪 Tech Stack

- **Backend:** Python 3.x + Flask
- **Frontend:** Jinja2 + Bootstrap 5
- **Database:** MySQL (via SQLAlchemy ORM)
- **Auth:** Flask sessions + Werkzeug password hashing
