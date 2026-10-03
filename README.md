# Student Q&A Forum

> **Môn học:** Python Web Development (PWD301)  
> **Đề tài (Topic 5):** Diễn đàn Hỏi - Đáp dành cho Sinh viên  
> **Công nghệ chính:** Flask | Bootstrap 5 | SQL Server | Docker  

---

## 1. Giới thiệu dự án 

**Student Q&A Forum** là một nền tảng diễn đàn Hỏi - Đáp học thuật trực tuyến dành cho sinh viên đại học (mô hình tương tự *Stack Overflow* thu nhỏ). 

Hệ thống hỗ trợ các tính năng chính:
- **Hỏi & Trả lời:** Sinh viên có thể đăng câu hỏi học tập có định dạng văn bản Markdown, gắn các thẻ môn học (tags) và viết câu trả lời cho các câu hỏi của sinh viên khác.
- **Bình chọn tương tác (Vote Up/Down):** Người dùng có thể bình chọn câu hỏi và câu trả lời hữu ích qua AJAX tức thì mà không cần tải lại trang.
- **Câu trả lời hay nhất (Best Answer):** Tác giả câu hỏi có thể đánh dấu "Best Answer" cho câu trả lời chuẩn xác nhất.
- **Hệ thống Điểm uy tín (Reputation):** Sinh viên tích lũy điểm khi nhận được bình chọn tích cực hoặc được chọn Best Answer.
- **Phân quyền người dùng (RBAC):** Phân chia rõ ràng các vai trò Sinh viên (Student), Kiểm duyệt viên (Moderator) và Quản trị viên (Admin).

---

## 2. Phân công nhiệm vụ nhóm

| Thành viên | Nhiệm vụ đảm nhiệm | Phạm vi tệp (Git Scope) |
| :--- | :--- | :--- |
| **Khánh** | Backend core & API | Toàn quyền Backend & App core |
| **Lam** | Giao diện người dùng (UI/UX & HTML) | `app/templates/` |
| **An** | Biểu mẫu & Dữ liệu mẫu (Form & Data) | `app/forms.py`, `seed_data.py` |
| **Trường** | Tích hợp AJAX, Deployment & Tài liệu dự án | `app/static/js/`, các file ngoài thư mục gốc |

---

## 3. Công nghệ sử dụng (Tech Stack)

- **Backend:** Python 3.11, [Flask 3.0.0](https://flask.palletsprojects.com/)
- **Cơ sở dữ liệu (Database):** SQL Server (kết hợp SQLite cho môi trường phát triển cục bộ)
- **ORM & Quản lý Migration:** Flask-SQLAlchemy 3.1.1, Flask-Migrate 4.0.5
- **Biểu mẫu & Xác thực dữ liệu:** Flask-WTF 1.2.1 (Tích hợp CSRF Protection)
- **Quản lý phiên & Xác thực:** Flask-Login 0.6.3, Flask-JWT-Extended 4.6.0
- **Bảo mật & Lọc mã độc:** Bleach 6.1.0 (Làm sạch HTML/Markdown chống XSS)
- **Frontend & Giao diện:** HTML5, CSS3, Bootstrap 5, JavaScript (Fetch API / AJAX không reload trang)
- **Đóng gói & Triển khai (Deployment):** Docker, Docker Compose

---

## 4. Hướng dẫn cài đặt & Khởi chạy (Setup Instructions)

### Điều kiện tiên quyết (Prerequisites)
Trước khi chạy dự án, máy tính cần cài sẵn các công cụ sau:
- Python 3.11 trở lên (kiểm tra bằng lệnh: `python --version`)
- Git (kiểm tra bằng lệnh: `git --version`)
- Docker Desktop (nếu muốn chạy ứng dụng qua container)


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

#### Bước 4: Khởi chạy máy chủ phát triển
```bash
python run.py
```
Truy cập ứng dụng tại: `http://127.0.0.1:5000`

---

### Cách 2: Khởi chạy nhanh bằng Docker (Khuyến nghị)

Nếu máy đã có **Docker** và **Docker Compose**, chỉ cần chạy một lệnh duy nhất:

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