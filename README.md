# IssueFlow

> A lightweight, full-stack bug and issue tracking system built with Python (FastAPI), SQLite, and Vanilla JavaScript.

**Live Application:** [https://issueflow-1.onrender.com/](https://issueflow-1.onrender.com/)

---

## Overview

IssueFlow is designed for developer teams and student project groups who need a fast, intuitive way to track bugs and tasks without the friction of bulky enterprise tools. 

It provides an agile Kanban workflow, full issue lifecycle management, real-time search and filtering, threaded team discussions, and an immutable audit trail for every change.

---

## Features

- **Agile Kanban Board**: 4-stage workflow (`Open`, `In Progress`, `Resolved`, `Closed`) with drag-and-drop card movement and quick filters for assigned tasks.
- **Search & Multi-Filter Catalog**: Filter issues by status, priority (`Low`, `Medium`, `High`, `Critical`), type (`Bug`, `Feature`, `Task`, `Improvement`), or assignee.
- **Audit History**: Every status transition, priority adjustment, and reassignment is automatically logged with author details and timestamps.
- **Discussion Threads**: Add comments directly to issues to collaborate on reproduction steps and fixes.
- **Dashboard Analytics**: Real-time project metrics including total issue counts, resolution rates, stage distributions, and recent team activity.
- **CSV Export**: Export filtered issue lists with one click for sprint reviews.
- **Authentication & Roles**: Secure bcrypt password hashing and JWT sessions, with pre-configured demo accounts for instant evaluation.

---

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, Pydantic v2
- **Database & ORM**: SQLite, SQLAlchemy 2.0 (with enforced foreign key constraints)
- **Frontend**: HTML5, Vanilla CSS (modern dark theme, responsive grid), Vanilla JavaScript
- **Testing & CI**: pytest, httpx (18 tests, 87% coverage), GitHub Actions

---

## Demo Accounts

The database comes pre-seeded with sample issues and test accounts for quick evaluation:

| Role | Name | Email | Password |
|---|---|---|---|
| **Team Lead / Admin** | Sarah Chen | `admin@issueflow.dev` | `admin123` |
| **Senior Engineer** | Alex Rivera | `alex@issueflow.dev` | `dev12345` |
| **QA Lead / Tester** | Priya Patel | `priya@issueflow.dev` | `qa123456` |
| **Frontend Engineer** | Marcus Vance | `marcus@issueflow.dev` | `front123` |

*(The sign-in modal also provides 1-click buttons to sign into any demo account without typing).*

---

## Local Setup

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/chandana-builds/IssueFlow.git
cd IssueFlow

# Create virtual environment
python -m venv .venv

# Activate environment
# On Windows:
.\.venv\Scripts\activate
# On macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
```

### 2. Run the Server

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Automated Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage reporting:
```bash
pytest --cov=backend --cov-report=term-missing
```

---

## License

This project is licensed under the MIT License.
