# IssueFlow

A lightweight, full-stack bug and issue tracking system built with Python (FastAPI), SQLAlchemy, and a vanilla JavaScript frontend. 

I built this project to solve a common problem small dev teams and hackathon squads face: heavy enterprise tools like Jira are often too bloated and slow for fast-paced development, while simple Kanban apps like Trello lack bug-tracking essentials (severity levels, audit trails, and reproducible bug reports).

IssueFlow gives you the sweet spot: an agile Kanban board, a searchable issue catalog, threaded discussions, and an automatic audit log for every change.

---

## What It Looks Like & Features

- **Agile Kanban Board**: 4-column board (`Open`, `In Progress`, `Resolved`, `Closed`) with drag-and-drop support and quick filters for assigned tasks.
- **Search & Multi-Filter Catalog**: Filter simultaneously by status, priority, type (Bug, Feature, Task, Improvement), or assignee. Real-time search across issue titles, keys, descriptions, and tags.
- **Live Audit Trail**: Every change (moving columns, reassigning developers, changing priority) is recorded as an immutable log entry with timestamps and author info.
- **Discussion Threads**: Team members can comment directly on issues with deletion controls (authors & admins only).
- **Dashboard Metrics**: High-level KPIs, resolution rates, an SVG donut breakdown by stage, and priority distribution bars.
- **CSV Export**: One-click download of filtered issues for sprint reviews and retrospectives.
- **Role-Based Auth & Quick Demo Switcher**: Secure bcrypt password hashing and JWT sessions. Includes pre-seeded demo accounts (Lead, Developer, QA) so anyone reviewing the repo can test workflows instantly with one click.

---

## Technical Stack & Architecture Decisions

```
IssueFlow/
├── backend/
│   ├── core/                  # Security (bcrypt, JWT) and FastAPI dependencies
│   ├── models/                # SQLAlchemy ORM models (User, Issue, Comment, ActivityLog)
│   ├── routers/               # API endpoints (/auth, /issues, /comments, /dashboard, /activities)
│   ├── schemas/               # Pydantic v2 schemas for request validation & response DTOs
│   ├── services/              # Business logic & database operations
│   ├── config.py              # Environment configuration (pydantic-settings)
│   ├── database.py            # SQLite engine, connection pooling, and FK pragmas
│   ├── main.py                # App entrypoint and static file mount
│   └── seed.py                # Demo database seeder
├── frontend/                  # Zero-build vanilla web client
│   ├── css/style.css          # Dark design system using CSS custom properties
│   ├── js/api.js              # Fetch client with auto JWT attachment
│   ├── js/app.js              # State management, drag-and-drop, modals & charts
│   └── index.html             # Single-page interface
├── tests/                     # Automated test suite (pytest + httpx)
├── .github/workflows/ci.yml   # Multi-version Python CI pipeline
├── pytest.ini
└── requirements.txt
```

### Why these technical choices?

1. **FastAPI over Flask or Django**:
   FastAPI gives us automatic OpenAPI/Swagger documentation at `/api/docs`, native validation via Pydantic v2, and clean dependency injection (`Depends(get_db)`, `Depends(get_current_user)`). It's fast to develop with and leaves zero ambiguity on schema types.

2. **SQLAlchemy 2.0 with Foreign Key Enforcement**:
   SQLite by default does not enforce foreign key constraints. In `backend/database.py`, I hooked an engine event listener (`PRAGMA foreign_keys=ON`) so deletions and relational integrity behave strictly like a production PostgreSQL instance.

3. **Audit History by Design**:
   Instead of just mutating columns, the `IssueService` diffs existing fields against updates. When a status or assignee changes, it writes both the updated record and an immutable `ActivityLog` row. This gives full accountability on who changed what without manual logging calls.

4. **Zero-Build Vanilla Frontend**:
   Instead of adding a heavy node_modules bundle with React or Tailwind build pipelines, I wrote the frontend with clean semantic HTML5, modern CSS (flexbox, grid, glassmorphism tokens), and vanilla JS. It loads instantly, has zero npm dependencies, and works out of the box when you start the Python server.

---

## Getting Started Locally

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Setup

```bash
# Clone the repository
git clone https://github.com/chandana-builds/IssueFlow.git
cd IssueFlow

# Create and activate a virtual environment
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
```

### 3. Run the App

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Once started:
- **Web App**: Visit `http://127.0.0.1:8000`
- **Swagger API Docs**: Visit `http://127.0.0.1:8000/api/docs`
- **Alternative ReDoc**: Visit `http://127.0.0.1:8000/api/redoc`

The database auto-seeds on first launch with sample users, issues, comments, and audit logs.

---

## Demo Accounts

If you want to test different roles without registering new accounts, use these pre-seeded logins:

| Role | Name | Email / Username | Password |
|---|---|---|---|
| **Admin / Team Lead** | Sarah Chen | `admin@issueflow.dev` (`admin`) | `admin123` |
| **Senior Developer** | Alex Rivera | `alex@issueflow.dev` (`alex_dev`) | `dev12345` |
| **QA Lead / Tester** | Priya Patel | `priya@issueflow.dev` (`priya_qa`) | `qa123456` |
| **Frontend Engineer** | Marcus Vance | `marcus@issueflow.dev` (`marcus_fe`) | `front123` |

> *Note: There are also 1-click login buttons on the sign-in modal in the UI.*

---

## Testing

The project includes unit and integration tests covering auth, CRUD operations, permission checks, search filters, and analytics calculations:

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=backend --cov-report=term-missing
```

All 18 tests pass with 87% coverage. Tests use an isolated in-memory SQLite database (`sqlite:///:memory:`) so your local development data is never altered.

---

## API Overview

| Method | Endpoint | Description | Auth |
|---|---|---|:---:|
| `POST` | `/api/auth/register` | Register new user | No |
| `POST` | `/api/auth/login` | Authenticate and get JWT | No |
| `GET` | `/api/auth/me` | Current user profile | Yes |
| `GET` | `/api/auth/users` | List active team members | No |
| `GET` | `/api/dashboard/stats` | KPI counters & chart data | Optional |
| `GET` | `/api/issues` | List issues (search & filter params) | No |
| `POST` | `/api/issues` | Create new issue (generates `ISF-X` key) | Yes |
| `GET` | `/api/issues/{id}` | Issue details, comments, and history | No |
| `PUT` | `/api/issues/{id}` | Update issue fields | Yes |
| `PATCH` | `/api/issues/{id}/status` | Move column / change status | Yes |
| `PATCH` | `/api/issues/{id}/assign` | Reassign issue | Yes |
| `DELETE` | `/api/issues/{id}` | Delete issue (author, manager, or admin) | Yes |
| `POST` | `/api/issues/{id}/comments` | Add comment to issue thread | Yes |
| `DELETE` | `/api/comments/{id}` | Delete comment (author or admin) | Yes |
| `GET` | `/api/issues/{id}/activities` | Get full audit log for an issue | No |
| `GET` | `/api/activities/recent` | Recent project-wide activity stream | No |
| `GET` | `/api/health` | Uptime check | No |

---

## CI / Automated Checks

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and pull request across Python 3.10 and 3.11, ensuring the test suite passes and generating coverage reports.

---

## License

MIT License. Free to use, fork, or build upon.
