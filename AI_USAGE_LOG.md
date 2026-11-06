# AI Usage Log - Nhật ký sử dụng AI

- Môn học: Python Web Development (PWD301)
- Đề tài: Topic 5 - Student Q&A Forum
- Mục đích: Ghi chép nhật ký sử dụng các công cụ Trí tuệ Nhân tạo (AI Tools) phục vụ quá trình phát triển dự án theo đúng Tiêu chí 10 trong Rubric đánh giá.

---

## 1. Nguyên tắc sử dụng AI của nhóm

1. AI đóng vai trò là trợ lý lập trình (Pair Programmer) hỗ trợ:
   - Gợi ý kiến trúc thư mục và mô hình tổ chức mã nguồn Flask chuẩn.
   - Hỗ trợ soạn thảo tài liệu kỹ thuật, đặc tả REST API và schema cơ sở dữ liệu.
   - Hỗ trợ kiểm tra lỗi, gỡ lỗi (debugging) và rà soát các tiêu chuẩn bảo mật.
2. Cam kết về tính trung thực và chất lượng:
   - Tất cả thành viên trong nhóm đều phải đọc hiểu từng dòng mã nguồn do AI gợi ý trước khi tích hợp vào dự án.
   - Thực hiện kiểm thử độc lập trên máy cục bộ và chịu trách nhiệm hoàn toàn về sản phẩm cuối cùng.

---

## 2. Nhật ký chi tiết (Prompt & Quality Assessment Log)

| Công cụ AI sử dụng | Mục đích tương tác | Câu lệnh đã dùng | Kết quả sinh ra | Đánh giá kết quả sinh ra |
| :--- | :--- | :--- | :--- | :--- |
| **Antigravity AI** | Soạn thảo tài liệu dự án và hướng dẫn thiết lập hệ thống | *"Tạo cấu trúc tài liệu README.md "* | Khung nội dung Markdown hoàn chỉnh: Giới thiệu đề tài, kiến trúc thư mục, Tech Stack và hướng dẫn cài đặt môi trường. | Kết quả rõ ràng, đúng chuẩn Markdown. Cần rà soát và điều chỉnh lại một số đường dẫn file cho khớp với thực tế mã nguồn nhóm phát triển. |
| **Antigravity AI** | Khắc phục lỗi hiển thị font Tiếng Việt khi chạy ứng dụng trong Docker | *"Lỗi Tiếng Việt (Phần cấu hình Docker) tôi fix đúng chưa, cần thêm những biến môi trường nào cho Dockerfile và docker-compose.yml?"* | Hướng dẫn cấu hình các biến môi trường chuẩn UTF-8 cho Linux container: `LANG=C.UTF-8`, `LC_ALL=C.UTF-8`, `PYTHONIOENCODING=utf-8` trong `Dockerfile` và `docker-compose.yml`. | Code cấu hình chính xác 100%, container nhận diện đúng bảng mã tiếng Việt có dấu khi kết nối và truy xuất dữ liệu từ SQL Server. |
| **Antigravity AI** | Khắc phục lỗi hiển thị lệch 7 giờ (Múi giờ UTC vs GMT+7) | *"Cách tạo Jinja filter để hiện thị đúng múi giờ, các template nào cần cập nhật thời gian?"* | Đoạn mã đăng ký Jinja template filter `@app.template_filter('vn_time')` sử dụng `timedelta(hours=7)` trong `app.py` và danh sách các file HTML cần áp dụng cú pháp filter (`index.html`, `question_detail.html`, `profile.html`, `admin_logs.html`). | Giải pháp tối ưu, xử lý ở tầng View/Presentation mà không làm thay đổi chuẩn UTC trong Database; hiển thị đúng giờ Việt Nam tại mọi trang. |
| **Antigravity AI** | Cải thiện trải nghiệm người dùng (UX) - Cảnh báo mất dữ liệu khi rời trang đặt câu hỏi | *"Hướng dẫn viết JavaScript bắt sự kiện beforeunload khi người dùng đang nhập dở tiêu đề hoặc nội dung ở trang /ask"* | Hàm JavaScript `initBeforeUnloadWarning()` trong `src/static/js/main.js`: kiểm tra giá trị của `#title` và `#content`, kích hoạt sự kiện `beforeunload` khi đóng tab/back trang và tự động bỏ qua khi bấm nút Đăng câu hỏi (Submit). | Hoạt động chính xác trên các trình duyệt Chrome/Edge/Firefox, ngăn chặn rủi ro mất nội dung do bấm nhầm thao tác. |

---

## 3. Đánh giá chất lượng mã nguồn do AI sinh ra

- **Tính đúng đắn**: Mã nguồn và cấu hình do AI đề xuất tuân thủ đúng cú pháp chuẩn của Python 3.11, Flask 3.0, Jinja2 và Docker Compose.
- **Tính an toàn**:
  - Không để lộ thông tin nhạy cảm (secret key, mật khẩu kết nối DB) trong mã nguồn, luôn khuyến nghị dùng biến môi trường `.env`.
  - Luôn kiểm tra tính hợp lệ của token CSRF đối với các thao tác người dùng.
- **Khả năng bảo trì**: Mã nguồn được module hóa rõ ràng, dễ đọc, có chú thích giải thích chi tiết từng hàm và dễ dàng mở rộng.
