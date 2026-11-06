# AI Usage Log

- **Course:** Python Web Development (PWD301)
- **Topic:** Topic 5 - Student Q&A Forum
- **Objective:** Document the usage of Artificial Intelligence (AI) tools throughout the project lifecycle in strict compliance with Criterion 10 of the Evaluation Rubric.

---

## 1. Team Principles for AI Utilization

1. **AI acts strictly as a Pair Programming Assistant to:**
   - Suggest best-practice Flask architectural structures (Blueprints, Application Factory pattern, Application Context).
   - Clarify technical standards, RESTful API specifications, and database query optimization principles.
   - Assist in reviewing and auditing web security standards (CSRF, XSS sanitization, SQL Injection prevention, IDOR, Session Security).
2. **Commitment to Academic Integrity and Quality Assurance:**
   - All team members must thoroughly comprehend, implement, test, and take complete responsibility for every line of code integrated into the project.
   - All features are independently verified on local environments with an automated suite of 50 Pytest test cases to ensure reliability and correctness.

---

## 2. Detailed Prompt & Quality Assessment Log

> *Note: Original prompts were conducted in Vietnamese and are preserved verbatim below to reflect authentic development logs.*

| Member | AI Tool | Purpose of Interaction | Prompt Used (Representative) | Generated Output | Quality Assessment & Student Verification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Lam** | **ChatGPT** | Consult on building layout with HTML, CSS, Bootstrap 5, and Jinja2 templates | *"Giải thích cách bố trí Navbar, Footer, Form và Card bằng Bootstrap 5."* | Provided architectural suggestions on responsive grid layout, navbar structure, and Jinja2 template inheritance | Guidance was clear and practical for UI/UX scope. All HTML/CSS coding, template structuring, and styling adjustments were performed manually. |
| | | Research UI/UX testing methodologies and responsive design across desktop and mobile devices | *"Hướng dẫn cách kiểm tra Responsive và trải nghiệm người dùng."* | Proposed testing criteria, viewport breakpoints, and Chrome DevTools emulation strategies | Recommendations were practical and successfully applied across multiple screen resolutions on both PC and mobile devices. |
| | | Diagnose and fix 3 UI issues: search empty-state alert, favicon 404, and email privacy on user profile | *"- Gợi ý cải thiện thông báo tìm kiếm chứa thuật ngữ 'seed dữ liệu'. - Giải thích nguyên nhân lỗi favicon 404 và cách khắc phục. - Hướng dẫn điều kiện hiển thị email trên trang Profile."* | Suggested solutions to address the search message wording, static favicon link tag, and Jinja conditional rendering for email privacy | All 3 UI issues were resolved and verified manually. AI provided explanatory guidance while template modifications were executed by the student. |
| **An** | **Claude** | Scaffold independent mock data generator (`seed_data.py`) | *"Nhóm đang làm về một web diễn đàn đặt câu hỏi và mình được giao nhiệm vụ với yêu cầu như ảnh, giờ hãy code sao cho có thể chạy được độc lập"* | Generated standalone Python script logic to seed mock questions and users | The initial script worked independently but lacked foreign key associations with other relational models due to isolated execution. |
| | **Antigravity AI** | Refine and connect `seed_data.py` relationships and complete `forms.py` validation | *"Kiểm tra file seed_data xem có thể hoạt động với các file khác không và kiểm tra file forms.py đã hoàn chỉnh chưa"* | Refined data seeding logic to properly wire User-Question-Answer relationships and added WTForms field validators | Successfully integrated data generator with SQLAlchemy models and stabilized form definitions across authentication flows. |
| | | Resolve pagination bug: questions duplicated between Page 1 and Page 2 | *"Hiện tại đang có lỗi: Câu hỏi bị trùng lặp giữa Trang 1 và Trang 2 do seed_data.py tạo 30 câu hỏi cùng thời điểm created_at. Hãy tìm và khắc phục lỗi trên trong file seed_data.py cho các câu hỏi có thời gian lùi dần cách nhau vài phút"* | Updated `seed_data.py` logic to stagger `created_at` timestamps incrementally backwards | Bug was completely resolved; SQL Server pagination with OFFSET...FETCH now stably orders questions chronologically without duplicates. |
| | | Implement student university email format validation filter | *"Thêm bộ lọc email: Mới áp dụng theo WTF, chưa có bộ lọc mail riêng. Đề xuất: Khóa lại chỉ cho đăng ký bằng mail edu (vd @*.edu.vn hoặc @*.edu) trên file forms.py"* | Added `STUDENT_EMAIL_REGEX` and `GENERAL_EMAIL_REGEX` with `Regexp` validators to `RegistrationForm` in `forms.py` | Effectively prevents spam accounts and enforces verified student identity (`.edu.vn` / `.edu`) for an academic forum. |
| **Trường** | **Antigravity AI** | Draft initial project documentation and setup guide (`README.md`) | *"Tạo cấu trúc tài liệu README.md"* | Outlined complete Markdown framework: project overview, directory structure, tech stack, and setup instructions | Clear structure that adhered to Markdown standards; paths and instructions were cross-checked and aligned with actual project structure. |
| | | Resolve Vietnamese UTF-8 font encoding issues in Docker Linux container | *"Lỗi Tiếng Việt (Phần cấu hình Docker) tôi fix đúng chưa, cần thêm những biến môi trường nào cho Dockerfile và docker-compose.yml?"* | Recommended configuring UTF-8 environment variables for Linux container (`LANG=C.UTF-8`, `LC_ALL=C.UTF-8`, `PYTHONIOENCODING=utf-8`) | 100% accurate; container properly renders and retrieves accented Vietnamese text when interacting with SQL Server. |
| | | Fix 7-hour timezone offset (UTC vs. Vietnam GMT+7) in Jinja templates | *"Cách tạo Jinja filter để hiện thị đúng múi giờ, các template nào cần cập nhật thời gian?"* | Provided Jinja template filter registration `@app.template_filter('vn_time')` using `timedelta(hours=7)` in `app.py` and template usage list | Optimal view-layer solution that maintains UTC standard in database while presenting accurate local Vietnam time to users. |
| | | Enhance UX: unsaved changes warning when leaving question creation page (`/ask`) | *"Hướng dẫn viết JavaScript bắt sự kiện beforeunload khi người dùng đang nhập dở tiêu đề hoặc nội dung ở trang /ask"* | JavaScript `initBeforeUnloadWarning()` in `src/static/js/main.js` intercepting `beforeunload` events when title/content inputs are non-empty | Works reliably across modern browsers, preventing accidental data loss upon navigation or tab closure. |
| **Khánh** | **Antigravity AI** | Consult on multi-tier RBAC architecture and custom `@permission_required` decorator implementation | *"Hướng dẫn cách viết custom decorator @permission_required trong Flask để kiểm tra quyền hạn chi tiết của người dùng và trả về mã lỗi 403 Forbidden nếu không đủ thẩm quyền."* | Provided standard decorator boilerplate using `functools.wraps`, querying `current_user.can()` and aborting with HTTP 403 | Well-structured reference. The student designed the `Permission` enum, constructed the `ROLE_PERMISSIONS` matrix, and integrated security auditing via `SecurityAuditLog`. |
| | | Investigate root cause of N+1 queries and optimization strategies in SQLAlchemy | *"Giải thích cách nhận biết lỗi N+1 queries khi hiển thị danh sách câu hỏi kèm thông tin tác giả/tags và hướng dẫn cách khắc phục bằng Eager Loading trong SQLAlchemy."* | Explained mechanics of Lazy Loading vs. Eager Loading, advising `joinedload` and `selectinload` to optimize SQL queries | Precise and actionable. The student audited all query endpoints, implemented eager loading on index and detail views, reducing queries from 61 down to 3 batch operations. |
| | | Review session security standards (OWASP) and Open Redirect vulnerability mitigation | *"Giải thích rủi ro của lỗ hổng Open Redirect qua tham số chuyển hướng next và gợi ý hàm kiểm tra URL an toàn phù hợp với Flask."* | Analyzed malicious redirect mechanics, recommending target URL host validation using `urllib.parse.urlsplit` | Accurate security insights. The student configured secure cookie parameters (`HttpOnly`, `SameSite='Lax'`, 2-hour timeout), enforced safe URL redirection in login, and implemented the password change flow. |
| | | Standardize RESTful API design conventions and 7 accurate HTTP status codes | *"Tư vấn danh sách các HTTP Status Codes phù hợp (200, 201, 400, 401, 403, 404, 500) cho từng thao tác CRUD của tài nguyên Question/Answer và cách xử lý lỗi toàn cục trong Flask."* | Provided RESTful status code mapping (201 Created on POST, 403 Forbidden on authorization failure, etc.) and global JSON error handler architecture | Fully compliant with REST standards. The student implemented all CRUD endpoint logic, IDOR ownership checks, dual authentication, and token expiration handling. |
| | | Structure isolated automated test suite using pure Pytest fixtures | *"Hướng dẫn cách tạo fixture client và app_ctx trong conftest.py để kiểm thử các route và API độc lập mà không ảnh hưởng cơ sở dữ liệu thực tế."* | Provided syntax examples for pytest fixtures and suggested SQLite in-memory database configuration for test isolation | Clear guidance enabling isolated test environments. The student authored 50 test cases covering Models, Decorators, Session, IDOR, and REST APIs with a 100% pass rate. |

---

## 3. Quality Assessment of AI-Generated Code

- **Correctness & Standards:** All code snippets, architectural recommendations, and configurations adhere to modern conventions for Python 3.11+, Flask 3.0, Jinja2, SQLAlchemy ORM, and Docker Compose.
- **Security & Integrity:**
  - Sensitive credentials (secret keys, database passwords) are strictly managed through `.env` and never hardcoded in repository files.
  - CSRF tokens are validated across all client state-changing forms.
  - User-generated HTML content is sanitized using `bleach` to eliminate Stored XSS threats.
  - ORM parameterized queries are used consistently to prevent SQL Injection vulnerabilities.
  - Strict ownership checks prevent Insecure Direct Object References (IDOR).
- **Maintainability & Architecture:** Codebase follows standard Flask Blueprint modular design, featuring comprehensive docstrings, pure pytest test cases, and clear separation of concerns across presentation, business logic, and persistence layers.
