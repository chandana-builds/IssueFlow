# IssueFlow — Smart Issue & Bug Tracking System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.31-d71f00.svg?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-2.8.2-e92063.svg?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![pytest](https://img.shields.io/badge/tests-18%20passed%20%7C%2087%25%20cov-brightgreen.svg?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF.svg?logo=github-actions&logoColor=white)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**IssueFlow** is a full-stack, production-ready software engineering project designed to help developers, student teams, and small software organizations efficiently report, manage, prioritize, and resolve software bugs and engineering tasks. 

Built with modern Python (**FastAPI**, **SQLAlchemy**, **Pydantic v2**, **SQLite**) and a responsive, sleek dark-themed frontend (**HTML5**, **Vanilla CSS**, **JavaScript**), IssueFlow provides an agile **Kanban Board**, real-time **Issue Audit History**, threaded **Discussion Comments**, multi-dimensional **Search & Filtering**, and an interactive **Analytics Dashboard**.

---

## 🌟 Key Features

### 1. 📊 Interactive Analytics Dashboard
- **KPI Summary Cards**: Real-time counters for Total Issues, Open/Backlog, In Progress, Resolution Rate, and Overdue tasks.
- **SVG Status Donut Chart**: Dynamic visual breakdown of issues by stage (`OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`).
- **Priority Distribution Bars**: Progress bars tracking issue density by severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- **Live Audit Activity Stream**: Recent timeline of team actions across the entire workspace.

### 2. 📋 Agile Kanban Board
- Visual 4-column agile board (`Open` &rarr; `In Progress` &rarr; `Resolved` &rarr; `Closed`).
- **Drag-and-Drop Workflow**: Seamlessly move cards across stages to immediately update status and record audit entries.
- Quick filtering for *"My Assigned"* tasks vs. *"All"* team tasks.

### 3. 🔍 Filterable Issue Catalog & Table
- Multi-parameter filtering toolbar: Filter by **Status**, **Priority**, **Type** (`BUG`, `FEATURE`, `TASK`, `IMPROVEMENT`), and **Assignee**.
- **Real-Time Search**: Instant search across issue keys (e.g. `ISF-1`), titles, descriptions, and tags.
- **One-Click CSV Export**: Download filtered issue lists for sprint reviews or retrospective meetings.

### 4. 🗂️ Detailed Issue Drawer & Collaboration
- Slide-over / modal drawer displaying complete issue metadata.
- **Inline Updating**: Instant status, priority, and assignee switches directly from the detail view.
- **Discussion Threads**: Add and delete comments with author timestamps and avatars.
- **Complete Audit Trail**: Dedicated audit history tab showing exact field transitions (e.g., *"Status changed from OPEN to IN_PROGRESS by Sarah Chen"*).

### 5. 🔐 Authentication & Role-Based Access
- Secure password hashing using **Bcrypt** with salt generation.
- **JWT (JSON Web Token)** Bearer authentication with configurable expiration.
- Pre-seeded **One-Click Demo Accounts** for immediate evaluation without typing credentials.

---

## 🏛️ System Architecture

IssueFlow follows a clean modular layered architecture with strict separation of concerns:

```
IssueFlow/
├── backend/
│   ├── core/                  # Security utilities & FastAPI dependencies
│   │   ├── dependencies.py    # JWT bearer verification & RBAC
│   │   └── security.py        # Bcrypt hashing & PyJWT token encoding/decoding
│   ├── models/                # SQLAlchemy database models
│   │   ├── activity.py        # Audit log entries
│   │   ├── comment.py         # Threaded comments
│   │   ├── issue.py           # Issue entity with key generation
│   │   └── user.py            # User credentials, roles, and profiles
│   ├── routers/               # FastAPI RESTful API endpoints
│   │   ├── activities.py      # /api/activities routes
│   │   ├── auth.py            # /api/auth routes (login, register, me, users)
│   │   ├── comments.py        # /api/issues/{id}/comments
│   │   ├── dashboard.py       # /api/dashboard/stats
│   │   └── issues.py          # /api/issues CRUD & transitions
│   ├── schemas/               # Pydantic v2 validation models & DTOs
│   ├── services/              # Business logic & database operations
│   │   ├── activity_service.py
│   │   ├── auth_service.py
│   │   ├── comment_service.py
│   │   ├── issue_service.py
│   │   └── stats_service.py
│   ├── config.py              # Pydantic-settings configuration
│   ├── database.py            # SQLite engine, sessionmaker, foreign key pragmas
│   ├── main.py                # FastAPI app initialization, static mount, lifespan
│   └── seed.py                # Sample demo data initializer
├── frontend/                  # Responsive web interface (Vanilla CSS & JS)
│   ├── css/
│   │   └── style.css          # Glassmorphism, dark theme, micro-animations
│   ├── js/
│   │   ├── api.js             # API wrapper & JWT token manager
│   │   └── app.js             # State, Kanban drag-and-drop, UI rendering
│   └── index.html             # Single-page application structure
├── tests/                     # Automated testing suite (pytest)
│   ├── conftest.py            # In-memory DB fixture & TestClient
│   ├── test_activities.py     # Audit trail test scenarios
│   ├── test_auth.py           # Authentication, JWT, and user management
│   ├── test_comments.py       # Comment addition & deletion permissions
│   ├── test_dashboard.py      # Analytics metrics calculation
│   └── test_issues.py         # Issue CRUD, search, filter, and lifecycle
├── .github/workflows/
│   └── ci.yml                 # GitHub Actions automated test & coverage matrix
├── pytest.ini                 # Pytest runner configuration
├── requirements.txt           # Core production dependencies
└── requirements-dev.txt       # Development & testing packages
```

---

## 🛠️ Technology Stack

| Layer | Technologies | Key Rationale |
|---|---|---|
| **Backend Framework** | Python 3.10+, FastAPI | High performance, auto OpenAPI/Swagger docs, native async support |
| **Validation & Schemas** | Pydantic v2 | Strict request/response typing and payload sanitization |
| **ORM & Database** | SQLAlchemy 2.0, SQLite | Robust relational mapping, foreign keys enabled (`PRAGMA foreign_keys=ON`) |
| **Security & Auth** | PyJWT, Bcrypt | Cryptographic salt hashing, stateless JWT session tokens |
| **Frontend** | HTML5, Vanilla CSS, Vanilla JS | Ultra-fast load times, glassmorphism design system, zero build tooling required |
| **Testing** | pytest, httpx, pytest-cov | 18 automated tests, 87% coverage across services and routes |
| **CI/CD** | GitHub Actions | Automated multi-version Python test matrix on every commit |

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/your-username/IssueFlow.git
cd IssueFlow

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.\.venv\Scripts\activate
# On macOS / Linux:
source .venv/bin/activate

# Install all dependencies (including dev/test tools)
pip install -r requirements-dev.txt
```

### 3. Run the Application

```bash
# Start the server (auto-seeds sample demo data on first launch)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser to:
- **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive API Documentation (Swagger UI)**: [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)
- **ReDoc Alternative API Docs**: [http://127.0.0.1:8000/api/redoc](http://127.0.0.1:8000/api/redoc)

---

## 👥 Demo Accounts (Pre-Seeded)

For rapid evaluation and grading, the database comes pre-populated with active team members:

| Role | Name | Email | Password |
|---|---|---|---|
| **Team Lead / Admin** | Sarah Chen | `admin@issueflow.dev` | `admin123` |
| **Senior Engineer** | Alex Rivera | `alex@issueflow.dev` | `dev12345` |
| **QA Lead / Tester** | Priya Patel | `priya@issueflow.dev` | `qa123456` |
| **Frontend Dev** | Marcus Vance | `marcus@issueflow.dev` | `front123` |

> 💡 **Tip:** The UI includes **1-Click Demo Buttons** on the sign-in modal to immediately switch between accounts with zero typing.

---

## 🧪 Automated Testing & Code Quality

IssueFlow has a comprehensive test suite written with `pytest` using an isolated in-memory SQLite database (`sqlite:///:memory:`) for guaranteed test determinism.

Run the full automated test suite:
```bash
pytest
```

Run test suite with detailed coverage report:
```bash
pytest --cov=backend --cov-report=term-missing
```

### Test Coverage Summary:
```
TOTAL: 18 passed in ~8s | 87% Code Coverage
- test_auth.py: Registration, duplicate detection, JWT generation, invalid credentials
- test_issues.py: Issue CRUD, ISF-key generation, search query, priority & assignee filters
- test_comments.py: Discussion thread creation, issue relationship, author deletion security
- test_activities.py: Automated audit log events on status/assignee modifications
- test_dashboard.py: Dynamic metric aggregation and resolution rate calculation
```

---

## 📡 REST API Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|:---:|
| `POST` | `/api/auth/register` | Register new user account | No |
| `POST` | `/api/auth/login` | Authenticate and obtain JWT token | No |
| `GET` | `/api/auth/me` | Fetch authenticated user profile | **Yes** |
| `GET` | `/api/auth/users` | List active team members | No |
| `GET` | `/api/dashboard/stats` | Aggregated dashboard analytics & charts data | Optional |
| `GET` | `/api/issues` | List issues (with search, filter, pagination) | No |
| `POST` | `/api/issues` | Create new issue with sequential key | **Yes** |
| `GET` | `/api/issues/{id}` | Retrieve issue details with comments & audit | No |
| `PUT` | `/api/issues/{id}` | Update issue fields | **Yes** |
| `PATCH` | `/api/issues/{id}/status` | Transition issue status (Kanban move) | **Yes** |
| `PATCH` | `/api/issues/{id}/assign` | Reassign issue to a team member | **Yes** |
| `DELETE` | `/api/issues/{id}` | Delete issue (reporter, manager, or admin) | **Yes** |
| `POST` | `/api/issues/{id}/comments` | Post comment to discussion thread | **Yes** |
| `DELETE` | `/api/comments/{id}` | Delete comment (author or admin) | **Yes** |
| `GET` | `/api/issues/{id}/activities` | Retrieve complete audit log for an issue | No |
| `GET` | `/api/activities/recent` | Retrieve global activity stream | No |
| `GET` | `/api/health` | Service health status | No |

---

## 🛡️ Software Engineering Principles

1. **Modular Separation**: Decoupled routers, database models, Pydantic schemas, and service layer logic.
2. **Defensive Validation**: Strict Pydantic v2 schemas reject malformed payloads before reaching the database.
3. **Data Integrity**: Enforced SQLite foreign keys via SQLAlchemy event hooks (`PRAGMA foreign_keys=ON`).
4. **Audit Trail**: Every significant lifecycle event (creation, status update, priority change, assignment) is captured in a dedicated immutable activity log table.
5. **Continuous Integration**: GitHub Actions workflow validates Python 3.10 and 3.11 test matrix on every commit.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
Developed for submission and presentation to the **Major League Hacking (MLH) Fellowship**.
