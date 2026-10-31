# Student Q&A Forum

> **Môn học:** Python Web Development (PWD301)  
> **Đề tài (Topic 5):** Diễn đàn Hỏi - Đáp dành cho Sinh viên  
> **Công nghệ chính:** Flask | Bootstrap 5 | SQL Server (pymssql) | Docker  

---

## 1. Giới thiệu dự án 

**Student Q&A Forum** là một nền tảng diễn đàn Hỏi - Đáp học thuật trực tuyến dành cho sinh viên đại học (mô hình tương tự *Stack Overflow* thu nhỏ). 

Hệ thống hỗ trợ các tính năng chính:
- **Hỏi & Trả lời:** Sinh viên có thể đăng câu hỏi học tập có định dạng văn bản Markdown, gắn các thẻ môn học (tags) và viết câu trả lời cho các câu hỏi của sinh viên khác.
- **Bình chọn tương tác (Vote Up/Down/Undo):** Người dùng có thể bình chọn câu trả lời hữu ích qua AJAX tức thì mà không cần tải lại trang. Hệ thống kiểm soát 1 người chỉ vote 1 lần và chống tự vote.
- **Sắp xếp & Phân trang:** Xem danh sách câu hỏi sắp xếp theo Mới nhất (`newest`) hoặc Nhiều vote nhất (`votes`), phân trang linh hoạt 20 mục/trang thông qua cấu hình `config.py`.
- **Phân quyền người dùng (RBAC 3 vai trò):** Phân chia rõ ràng các vai trò Sinh viên (Student), Kiểm duyệt viên (Moderator) và Quản trị viên (Admin) kèm theo cơ chế bảo vệ quyền sở hữu (chống IDOR).
- **Nhật ký kiểm toán an ninh (Security Audit Log):** Ghi nhận các sự kiện xác thực, phát hiện nỗ lực spam, truy cập trái phép 403, lỗi 404, CSRF và hỗ trợ Dashboard giám sát thời gian thực (Live Monitoring).

---

## 2. Phân công nhiệm vụ nhóm

| Thành viên | Nhiệm vụ đảm nhiệm | Phạm vi tệp (Git Scope) |
| :--- | :--- | :--- |
| **Khánh** | Backend core, API & Bảo mật | Toàn quyền Backend & App core |
| **Lam** | Giao diện người dùng (UI/UX & HTML) | `src/templates/` |
| **An** | Biểu mẫu & Dữ liệu mẫu (Form & Data) | `src/forms.py`, `seed_data.py` |
| **Trường** | Tích hợp AJAX, Deployment & Tài liệu dự án | `src/static/js/`, các file cấu hình gốc |

---

## 3. Công nghệ sử dụng (Tech Stack)

- **Backend:** Python 3.11+, [Flask 3.0.0](https://flask.palletsprojects.com/)
- **Cơ sở dữ liệu (Database):** Microsoft SQL Server (kết nối trực tiếp qua TCP/IP bằng `pymssql`, không phụ thuộc ODBC)
- **ORM & Quản lý Migration:** Flask-SQLAlchemy 3.1.1, Flask-Migrate 4.0.5
- **Biểu mẫu & Xác thực dữ liệu:** Flask-WTF 1.2.1 (Tích hợp CSRF Protection & Server-side validation)
- **Quản lý phiên & Xác thực:** Flask-Login 0.6.3, Flask-JWT-Extended 4.6.0, `werkzeug.security` (scrypt password hashing)
- **Bảo mật & Lọc mã độc:** Bleach 6.1.0 (Làm sạch HTML/Markdown chống XSS)
- **Frontend & Giao diện:** HTML5, CSS3, Bootstrap 5.3, JavaScript Fetch API (AJAX không reload trang)
- **Đóng gói & Triển khai (Deployment):** Docker, Docker Compose

---

## 4. Cấu trúc thư mục dự án (Project Directory Structure)

```text
pwd301_qa_forum/
│
├── app.py                      # Điểm khởi chạy ứng dụng Flask chính, cấu hình Blueprints & Error handlers
├── config.py                   # Cấu hình tập trung (Classes: Config, Dev, Test, Prod), connection pool, phân trang
├── seed_data.py                # Script sinh dữ liệu mẫu (Faker) cho Users, Tags, Questions, Answers
├── requirements.txt            # Danh sách các thư viện phụ thuộc Python
├── Dockerfile                  # Đóng gói container ứng dụng web Flask
├── docker-compose.yml          # Điều phối container web và liên kết SQL Server
├── AI_USAGE_LOG.md             # Nhật ký sử dụng AI hỗ trợ theo Tiêu chí 10 Rubric
├── README.md                   # Tài liệu hướng dẫn cài đặt và tổng quan dự án
│
├── src/                        # Thư mục mã nguồn chính của ứng dụng
│   ├── __init__.py             # Đánh dấu package Python
│   ├── models.py               # Các model SQLAlchemy (User, Question, Answer, Tag, Vote, SecurityAuditLog)
│   ├── forms.py                # Các biểu mẫu Flask-WTF tích hợp CSRF & server-side validation
│   ├── extensions.py           # Tiện ích Flask (LoginManager)
│   ├── auth.py                 # Blueprint 'auth': Đăng ký, đăng nhập, phân quyền RBAC, profile, admin dashboard
│   ├── main.py                 # Blueprint 'main': Trang chủ, hỏi đáp, phân trang, lọc/tìm kiếm, sắp xếp votes
│   ├── api.py                  # Blueprint 'api': Các REST API endpoints (Questions, Tags, Vote AJAX, Live Logs)
│   │
│   ├── templates/              # Thư mục giao diện HTML (Jinja2 Template Inheritance)
│   │   ├── base.html           # Khung layout chung, navbar, footer, flash messages
│   │   ├── index.html          # Trang chủ danh sách câu hỏi, thanh phân trang, lọc tag & sắp xếp
│   │   ├── question_detail.html# Chi tiết câu hỏi, danh sách câu trả lời, nút vote AJAX, nút xóa bài
│   │   ├── ask_question.html   # Form đặt câu hỏi mới có chống XSS (Bleach) và chống Spam
│   │   ├── login.html          # Form đăng nhập tài khoản
│   │   ├── register.html       # Form đăng ký tài khoản sinh viên
│   │   ├── profile.html        # Trang hồ sơ cá nhân và lịch sử hoạt động
│   │   ├── admin_logs.html     # Dashboard giám sát nhật ký an ninh thời gian thực (Live Monitoring)
│   │   └── error.html          # Trang hiển thị thông báo lỗi (403, 404, 500, CSRF)
│   │
│   └── static/                 # Tài nguyên tĩnh (CSS, JS, hình ảnh)
│       ├── css/
│       │   └── style.css       # Tùy biến kiểu dáng giao diện
│       └── js/
│           ├── main.js         # JavaScript chung: xử lý vote AJAX không tải lại trang, CSRF token
│           └── admin_logs.js   # JavaScript chuyên biệt: Live polling 3s cho Dashboard Admin
│
└── tests/                      # Bộ kiểm thử tự động (Unit Tests)
    ├── __init__.py             # Package tests
    ├── test_models.py          # Kiểm thử Models & thuật toán băm mật khẩu Werkzeug
    ├── test_routes.py          # Kiểm thử các Routes giao diện, RBAC phân quyền và chống lỗi IDOR
    └── test_api.py             # Kiểm thử các REST API endpoints & luồng bình chọn (Vote Flow)
```

---

## 5. Hướng dẫn cài đặt & Khởi chạy (Setup Instructions)

### Điều kiện tiên quyết (Prerequisites)
- Python 3.11 trở lên (`python --version`)
- Git (`git --version`)
- Microsoft SQL Server đã bật xác thực SQL Server Authentication (cổng TCP/IP 1433)
- Docker Desktop (nếu muốn khởi chạy qua container)

---

### Cách 1: Khởi chạy trên máy cục bộ (Local Development)

#### Bước 1: Kéo mã nguồn về máy
```bash
git clone https://github.com/DangLamMyKhanh/pwd301_qa_forum.git
cd pwd301_qa_forum
```

#### Bước 2: Tạo và kích hoạt môi trường ảo (Virtualenv)
- **Trên Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **Trên macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

#### Bước 3: Cài đặt các thư viện phụ thuộc
```bash
pip install -r requirements.txt
```

#### Bước 4: Tạo cơ sở dữ liệu và nạp dữ liệu mẫu (Seed Data)
```bash
python seed_data.py
```

#### Bước 5: Khởi chạy máy chủ phát triển
```bash
python app.py
```
Truy cập ứng dụng tại: `http://127.0.0.1:5000`

---

### Cách 2: Khởi chạy nhanh bằng Docker (Khuyến nghị)

Nếu máy đã có **Docker** và **Docker Compose**, chỉ cần chạy lệnh:

```bash
docker-compose up -d --build
```
*(Hoặc dùng lệnh `docker compose up -d --build` tùy phiên bản Docker)*

- Để xem log hoạt động của container:
  ```bash
  docker-compose logs -f
  ```
- Để tắt ứng dụng:
  ```bash
  docker-compose down
  ```
Sau khi khởi động thành công, mở trình duyệt và truy cập: `http://localhost:5000`

---

## 6. Tài khoản kiểm thử mẫu (Demo Accounts)

Hệ thống đã nạp sẵn 3 nhóm tài khoản tương ứng với 3 vai trò phân quyền (RBAC):

| Vai trò (Role) | Username | Email | Mật khẩu mặc định | Quyền hạn đặc trưng |
| :--- | :--- | :--- | :---: | :--- |
| **Admin** | `admin` | `admin@student.edu.vn` | `123456` | Toàn quyền, xem Dashboard Logs bảo mật thời gian thực, xóa bài |
| **Moderator** | `moderator` | `moderator@student.edu.vn` | `123456` | Kiểm duyệt: Xóa các câu hỏi / câu trả lời vi phạm quy chuẩn |
| **Student** | 15 sinh viên mẫu | `...` | `123456` | Đăng câu hỏi, trả lời, vote, chỉ được quản lý bài viết của chính mình |

---

## 7. Chạy kiểm thử tự động (Unit Tests)

Dự án tích hợp sẵn bộ kiểm thử đơn vị với 17 test cases bao phủ toàn diện Models, Routes, RBAC, IDOR và REST API:

```powershell
python -m unittest discover tests
```
Kết quả kỳ vọng: **17/17 tests OK (100% Passed)**.