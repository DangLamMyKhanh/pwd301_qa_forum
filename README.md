# Student Q&A Forum

> **Course:** Python Web Development (PWD301)  
> **Topic (Topic 5):** Academic Q&A Forum for University Students  
> **Core Technologies:** Flask 3.0 | Bootstrap 5 | Microsoft SQL Server (`pymssql`) | Docker | Pytest  

---

## 1. Project Overview

**Student Q&A Forum** is an online academic question-and-answer platform tailored for university students (inspired by a streamlined *Stack Overflow* architecture). It provides an interactive, secure, and modern collaborative environment for students and faculty.

### Key Supported Features:
- **Questions & Answers:** Students can post academic questions with Markdown formatting, tag related academic subjects/topics, and submit answers to peer questions.
- **Interactive Voting (AJAX Upvote / Downvote / Undo):** Users can vote on helpful questions and answers instantly via AJAX without page reloads. The system strictly enforces single-vote limits per user and prevents self-voting.
- **Mark "Best Answer":** Question authors can designate the most helpful answer as the "Best Answer" with real-time AJAX toggling and visual badge highlights.
- **Reputation Points System:** Gamification system that dynamically rewards or penalizes users based on community engagement:
  - Upvoted question/answer: **+10 points**
  - Downvoted question/answer: **-5 points**
  - Accepted "Best Answer": **+15 points**
- **Two-Tier Role-Based Access Control (RBAC):** Strict permission hierarchy enforced by custom decorators:
  - **Admin:** Complete forum oversight, permanent post deletion, discussion locking/unlocking (`is_locked`), and access to the live Security Audit Log dashboard.
  - **Moderator:** Content moderation to hide/unhide violating questions and answers (`is_hidden`) without deleting data.
  - **Student:** Ask questions, write answers, vote, select Best Answer on own questions, and delete own posts (IDOR protected).
- **Custom Authorization Decorators:** Custom `@role_required(*roles)` and `@permission_required(*permissions)` decorators that automatically intercept unauthorized requests, log violations to `SecurityAuditLog`, and abort with `403 Forbidden`.
- **Database Query Optimization (N+1 Prevention):** Implements SQLAlchemy Eager Loading (`joinedload` for one-to-one author relationships, `selectinload` for tags and answers), reducing database queries on the homepage from 61 down to just 3 batch queries.
- **Comprehensive Session & Authentication Security:**
  - Secure session cookies (`HttpOnly=True`, `SameSite='Lax'`, 2-hour timeout).
  - "Remember Me" functionality (14-day persistent login with `HttpOnly` cookie).
  - Open Redirect prevention on login (`?next` validation).
  - Password change functionality with old password verification.
- **Standard RESTful API:**
  - Minimum 15+ standard RESTful endpoints.
  - Full HTTP methods: `GET`, `POST`, `PUT`, `DELETE`.
  - Accurate HTTP status codes: **`200 OK`**, **`201 Created`**, **`400 Bad Request`**, **`401 Unauthorized`**, **`403 Forbidden`**, **`404 Not Found`**, and **`500 Internal Server Error`**.
  - Dual Authentication: JWT Bearer Token (`Authorization: Bearer <token>`) with configured token expiry (`JWT_ACCESS_TOKEN_EXPIRES`) and session-cookie fallback.
- **Defense-in-Depth Input Validation:**
  - **Client-Side:** HTML5 constraints (`required`, `minlength`, `maxlength`, `pattern`, `type="email"`) and JavaScript real-time validation for student emails and matching passwords.
  - **Server-Side:** Flask-WTF validators (`DataRequired`, `Length`, `Regexp`, `EqualTo`) and HTML sanitization using `bleach` against Cross-Site Scripting (XSS).
- **Security Audit Logging & Live Monitoring:** Tracks authentication events, spam attempts, 403 authorization failures, 404 scans, 500 errors, and CSRF attacks with a 3-second live polling dashboard for administrators.

---

## 2. Team Member Responsibilities

| Member | Assigned Role & Responsibilities | File Scope (Git Scope) |
| :--- | :--- | :--- |
| **Khánh** | Backend Core, Database ORM, RBAC & API Security | App core, `src/models.py`, `src/auth.py`, `src/api.py`, `config.py` |
| **Lam** | User Interface & HTML Templates (UI/UX) | `src/templates/` (`index.html`, `question_detail.html`, etc.) |
| **An** | Web Forms, Validation & Database Seeding | `src/forms.py`, `seed_data.py` |
| **Trường** | AJAX Integration, Deployment & Documentation | `src/static/js/`, Docker configuration, `AI_USAGE_LOG.md`, `README.md` |

---

## 3. Technology Stack

- **Backend Framework:** Python 3.11+, [Flask 3.0.0](https://flask.palletsprojects.com/)
- **Database Engine:** Microsoft SQL Server (direct TCP/IP connection via `pymssql`, driver-free without ODBC dependencies)
- **ORM & Database Migrations:** Flask-SQLAlchemy 3.1.1, Flask-Migrate 4.0.5
- **Forms & Data Validation:** Flask-WTF 1.2.1 (integrated CSRF Protection & server-side validation)
- **Authentication & Sessions:** Flask-Login 0.6.3, Flask-JWT-Extended 4.6.0, `werkzeug.security` (scrypt password hashing)
- **Security & Sanitization:** Bleach 6.1.0 (HTML/Markdown content sanitization against XSS)
- **Frontend & UI:** HTML5, CSS3, Bootstrap 5.3, JavaScript Fetch API (AJAX without page reload)
- **Containerization & Deployment:** Docker, Docker Compose
- **Test Automation:** Pytest 9.2+ (100% pure pytest fixtures & assertions)

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
├── pytest.ini                  # Pytest configuration (-v --tb=short)
├── AI_USAGE_LOG.md             # AI usage log compliant with Rubric Criterion 10 (5-column format)
├── README.md                   # Project documentation and setup guide (English)
│
├── src/                        # Core application source code
│   ├── __init__.py             # Python package marker
│   ├── models.py               # SQLAlchemy models (User, Question, Answer, Tag, Vote, SecurityAuditLog, Permission)
│   ├── forms.py                # Flask-WTF forms with CSRF & server-side validation
│   ├── extensions.py           # Flask extensions (LoginManager)
│   ├── auth.py                 # 'auth' Blueprint: Register, Login, Change Password, RBAC decorators, admin dashboard
│   ├── main.py                 # 'main' Blueprint: Homepage, Q&A, pagination, tag filtering, vote sorting, Best Answer
│   ├── api.py                  # 'api' Blueprint: REST API endpoints (Questions, Answers, Vote AJAX, JWT Auth, Live Logs)
│   │
│   ├── templates/              # HTML templates (Jinja2 Template Inheritance)
│   │   ├── base.html           # Shared layout, navbar with reputation star, footer, flash messages
│   │   ├── index.html          # Question feed homepage, pagination bar, tag filter & vote sorting
│   │   ├── question_detail.html# Question details, answer list, Best Answer selection, AJAX vote buttons
│   │   ├── ask_question.html   # New question form with XSS protection (Bleach) and unsaved changes alert
│   │   ├── login.html          # Account login form with Remember Me
│   │   ├── register.html       # Student registration form with student email validation
│   │   ├── profile.html        # User profile page, reputation score, and activity history
│   │   ├── change_password.html# Password change form with client/server validation
│   │   ├── admin_logs.html     # Real-time security audit log monitoring dashboard (3s live polling)
│   │   └── error.html          # Error pages (400, 401, 403, 404, 500, CSRF)
│   │
│   └── static/                 # Static assets (CSS, JS, images)
│       ├── css/
│       │   └── style.css       # Custom stylesheet overrides
│       └── js/
│           ├── main.js         # Shared client-side JS: AJAX voting, Best Answer, form validation, beforeunload prompt
│           └── admin_logs.js   # Admin dashboard JS: 3-second live polling for security logs
│
└── tests/                      # Automated unit test suite (50 test cases, 100% pure pytest)
    ├── __init__.py             # Tests package marker
    ├── conftest.py             # Pytest fixtures (`client`, `app_ctx`) and application context setup
    ├── test_models.py          # Unit tests for Models, Werkzeug password hashing, RBAC permission matrix
    ├── test_routes.py          # Unit tests for UI routes, RBAC decorators, IDOR prevention, sessions, CSRF
    └── test_api.py             # Unit tests for REST API endpoints, 7 HTTP status codes, JWT auth & token expiry
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
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **On macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
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

## 6. RBAC Permissions & Demo Accounts

The system implements a two-tier access control model (Role-Based & Permission-Based Access Control) defined in `src/models.py` (`Permission` class and `ROLE_PERMISSIONS` matrix) and enforced via `@role_required` and `@permission_required` in `src/auth.py`.

### Demo Accounts

The system comes pre-seeded with accounts covering all 3 RBAC roles:

| Role | Username | Email | Default Password | Permissions & Features (Rubric Topic 5) |
| :--- | :--- | :--- | :---: | :--- |
| **Admin** | `admin` | `admin@student.edu.vn` | `123456` | Full administrative access, delete any post, lock/unlock discussions (`is_locked`), real-time Security Audit Log dashboard |
| **Moderator** | `moderator` | `moderator@student.edu.vn` | `123456` | Content moderation: hide/unhide violating questions or answers (`is_hidden`) without permanent deletion |
| **Student** | 15 sample students | `...` | `123456` | Ask questions, write answers, vote via AJAX, mark Best Answer on own questions, accumulate reputation points |

---

## 7. Running Automated Tests (Unit Tests)

The project includes an automated test suite with **50 comprehensive test cases** covering all rubric criteria (**CLO6, CLO7**):
- **Model Tests (`tests/test_models.py`):** Werkzeug scrypt password hashing verification, Many-to-Many Question-Tag relationships, and the complete RBAC permission matrix for Student, Moderator, and Admin roles.
- **Route & Security Tests (`tests/test_routes.py`):** UI page rendering, vote sorting (`?sort=votes`), mandatory login redirection (302), custom 404 handler, CSRF token enforcement (400 on missing token), session security settings (HttpOnly, Lax, Timeout), open redirect protection, password change flow, custom decorators (`@role_required`, `@permission_required`), and IDOR protection.
- **REST API & Status Code Tests (`tests/test_api.py`):**
  - Verification of all 7 accurate HTTP status codes: **`200 OK`**, **`201 Created`**, **`400 Bad Request`**, **`401 Unauthorized`**, **`403 Forbidden`**, **`404 Not Found`**, and **`500 Internal Server Error`**.
  - Verification of all standard RESTful verbs: **`GET`**, **`POST`**, **`PUT`**, and **`DELETE`**.
  - Dual authentication testing via **JWT Bearer Token** (`Authorization: Bearer <token>`), Token Expiry rejection (401), invalid signature rejection (401), and Session Cookies.
  - Interactive voting workflows (single-vote enforcement, undo), Best Answer selection (+15 reputation), and role-based lock/hide API endpoints.
- **Flask Test Client:** Built with pure pytest fixtures (`client`, `app_ctx` in `tests/conftest.py`) without legacy `unittest` dependencies.

To execute the test suite with **pytest**:

```powershell
pytest
```

Expected result: **50/50 passed (100% Passed)**.
