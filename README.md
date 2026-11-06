# Student Q&A Forum

> **Course:** Python Web Development (PWD301)  
> **Topic (Topic 5):** Student Q&A Forum  
> **Core Technologies:** Flask | Bootstrap 5 | SQL Server (pymssql) | Docker  

---

## 1. Project Overview

**Student Q&A Forum** is an online academic question-and-answer platform tailored for university students (inspired by a streamlined *Stack Overflow* architecture).

Key supported features:
- **Questions & Answers:** Students can post academic questions with Markdown formatting, tag related academic subjects/topics, and submit answers to peer questions.
- **Interactive Voting (Upvote / Downvote / Undo):** Users can vote on helpful answers instantly via AJAX without page reloads. Includes single-vote enforcement per user and prevents self-voting.
- **Sorting & Pagination:** Browse questions sorted by Newest (`newest`) or Most Voted (`votes`), with configurable pagination (20 items/page via `config.py`).
- **Role-Based Access Control (3 RBAC Roles):** Clear separation between Student, Moderator, and Admin roles, complete with ownership verification (IDOR prevention).
- **Security Audit Logging:** Logs authentication events, anti-spam rate limiting triggers, unauthorized 403 access attempts, 404 errors, and CSRF violations, supported by a real-time Live Monitoring Dashboard.

---

## 2. Team Member Responsibilities

| Member | Assigned Role & Responsibilities | File Scope (Git Scope) |
| :--- | :--- | :--- |
| **Khánh** | Backend Core, API & Security | Full App Core & Backend |
| **Lam** | User Interface (UI/UX & HTML) | `src/templates/` |
| **An** | Forms & Sample Seed Data | `src/forms.py`, `seed_data.py` |
| **Trường** | AJAX Integration, Deployment & Documentation | `src/static/js/`, Root configuration files |

---

## 3. Technology Stack

- **Backend:** Python 3.11+, [Flask 3.0.0](https://flask.palletsprojects.com/)
- **Database:** Microsoft SQL Server (direct TCP/IP connection via `pymssql`, driver-free without ODBC dependencies)
- **ORM & Migrations:** Flask-SQLAlchemy 3.1.1, Flask-Migrate 4.0.5
- **Web Forms & Validation:** Flask-WTF 1.2.1 (integrated CSRF Protection & server-side validation)
- **Authentication & Sessions:** Flask-Login 0.6.3, Flask-JWT-Extended 4.6.0, `werkzeug.security` (scrypt password hashing)
- **Security & Sanitization:** Bleach 6.1.0 (HTML/Markdown sanitization against XSS)
- **Frontend & UI:** HTML5, CSS3, Bootstrap 5.3, JavaScript Fetch API (AJAX without page reload)
- **Containerization & Deployment:** Docker, Docker Compose

---

## 4. Project Directory Structure

```text
pwd301_qa_forum/
│
├── app.py                      # Main Flask application entry point, Blueprints & Error handlers registration
├── config.py                   # Centralized configuration (Config, Dev, Test, Prod), connection pool, pagination
├── seed_data.py                # Database seeding script (Faker) for Users, Tags, Questions, and Answers
├── requirements.txt            # Python dependency specifications
├── Dockerfile                  # Container packaging for Flask web application
├── docker-compose.yml          # Container orchestration linking Web app with SQL Server
├── AI_USAGE_LOG.md             # AI usage log compliant with Rubric Criterion 10
├── README.md                   # Project documentation and setup guide
│
├── src/                        # Core application source code
│   ├── __init__.py             # Python package marker
│   ├── models.py               # SQLAlchemy models (User, Question, Answer, Tag, Vote, SecurityAuditLog)
│   ├── forms.py                # Flask-WTF forms with CSRF & server-side validation
│   ├── extensions.py           # Flask extensions (LoginManager)
│   ├── auth.py                 # 'auth' Blueprint: Register, Login, RBAC authorization, profile, admin dashboard
│   ├── main.py                 # 'main' Blueprint: Homepage, Q&A, pagination, tag filtering, vote sorting
│   ├── api.py                  # 'api' Blueprint: REST API endpoints (Questions, Tags, Vote AJAX, Live Logs)
│   │
│   ├── templates/              # HTML templates (Jinja2 Template Inheritance)
│   │   ├── base.html           # Shared layout, navbar, footer, flash messages
│   │   ├── index.html          # Question feed homepage, pagination bar, tag filter & sorting
│   │   ├── question_detail.html# Question details, answer list, AJAX vote buttons, delete actions
│   │   ├── ask_question.html   # New question form with XSS protection (Bleach) and anti-spam
│   │   ├── login.html          # Account login form
│   │   ├── register.html       # Student registration form
│   │   ├── profile.html        # User profile page and activity history
│   │   ├── admin_logs.html     # Real-time security audit log monitoring dashboard
│   │   └── error.html          # Error pages (403, 404, 500, CSRF)
│   │
│   └── static/                 # Static assets (CSS, JS, images)
│       ├── css/
│       │   └── style.css       # Custom stylesheet overrides
│       └── js/
│           ├── main.js         # Shared client-side JS: AJAX voting, CSRF handling, beforeunload prompt
│           └── admin_logs.js   # Admin dashboard JS: 3-second live polling for security logs
│
└── tests/                      # Automated unit test suite
    ├── __init__.py             # Tests package marker
    ├── conftest.py             # Pytest fixtures and test client configuration
    ├── test_models.py          # Unit tests for Models & Werkzeug password hashing
    ├── test_routes.py          # Unit tests for UI routes, RBAC authorization, and IDOR prevention
    └── test_api.py             # Unit tests for REST API endpoints & Voting workflow
```

---

## 5. Setup & Installation Instructions

### Prerequisites
- Python 3.11 or higher (`python --version`)
- Git (`git --version`)
- Microsoft SQL Server with SQL Server Authentication enabled (TCP/IP port 1433)
- Docker Desktop (if deploying via containers)

---

### Method 1: Local Development Setup

#### Step 1: Clone the repository
```bash
git clone https://github.com/DangLamMyKhanh/pwd301_qa_forum.git
cd pwd301_qa_forum
```

#### Step 2: Create and activate a Virtual Environment (venv)
- **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

#### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Initialize database and seed sample data
```bash
python seed_data.py
```

#### Step 5: Start the development server
```bash
python app.py
```
Open your browser and navigate to: `http://127.0.0.1:5000`

---

### Method 2: Quick Start with Docker (Recommended)

If you have **Docker** and **Docker Compose** installed:

```bash
docker-compose up -d --build
```
*(Or `docker compose up -d --build` depending on your Docker version)*

- To view container logs:
  ```bash
  docker-compose logs -f
  ```
- To stop the application:
  ```bash
  docker-compose down
  ```
Once running, open your browser and navigate to: `http://localhost:5000`

---

## 6. Demo Accounts for Testing

The system comes pre-seeded with accounts covering all 3 RBAC roles:

| Role | Username | Email | Default Password | Permissions & Features |
| :--- | :--- | :--- | :---: | :--- |
| **Admin** | `admin` | `admin@student.edu.vn` | `123456` | Full access, real-time security log dashboard, delete any post |
| **Moderator** | `moderator` | `moderator@student.edu.vn` | `123456` | Content moderation: delete inappropriate questions/answers |
| **Student** | 15 sample students | `...` | `123456` | Post questions, write answers, vote, manage own posts only |

---

## 7. Running Automated Tests (Unit Tests)

The project includes an automated test suite with 17 comprehensive test cases covering Models, Routes, RBAC, IDOR protection, and REST APIs using **pytest** (compliant with Rubric Criterion 9):

```powershell
pytest
```
*(Or via the built-in runner: `python -m unittest discover tests`)*

Expected result: **17 passed (100% Passed)**.
