import os
from flask import Flask, request, render_template
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_migrate import Migrate
from flask_login import current_user
from flask_jwt_extended import JWTManager

from config import Config
from src.models import db, User, SecurityAuditLog
from src.extensions import login_manager

app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
app.config.from_object(Config)

# Khởi tạo các tiện ích với App
jwt = JWTManager(app)
db.init_app(app)
migrate = Migrate(app, db)
login_manager.init_app(app)
csrf = CSRFProtect(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# đăng ký các blueprint
from src.auth import auth_bp
from src.api import api_bp
from src.main import main_bp
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

# Miễn trừ CSRF cho API Blueprint để các hàm fetch AJAX (như vote) hoạt động được
csrf.exempt(api_bp)


# ==========================================
# HÀM HỖ TRỢ GHI LOG BẢO MẬT VÀO DATABASE
# ==========================================
def log_security_event(action):
    """Ghi nhận sự kiện bảo mật vào bảng SecurityAuditLog trong Database"""
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        ip_addr = request.remote_addr or 'Unknown'
        log = SecurityAuditLog(
            user_id=user_id,
            ip_address=ip_addr,
            action=action
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[SECURITY LOG ERROR] Không thể ghi log vào database: {e}")


# ==========================================
# XỬ LÝ LỖI TOÀN CỤC & GHI LOG BẢO MẬT
# ==========================================
@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    # 1. Ghi log cảnh báo tấn công / lỗi CSRF
    log_security_event(f"CSRF Attack/Error: {error.description} (URL: {request.path})")
    return render_template(
        'error.html',
        code=400,
        title="Yêu cầu không hợp lệ (CSRF Error)",
        message=f"Hệ thống phát hiện lỗi bảo mật CSRF: {error.description}. Vui lòng thử tải lại trang hoặc kiểm tra token."
    ), 400


@app.errorhandler(404)
def not_found(error):
    # 2. Ghi log khi quét / truy cập đường dẫn không tồn tại
    log_security_event(f"404 Not Found: {request.path}")
    return render_template(
        'error.html',
        code=404,
        title="Trang không tồn tại",
        message=f"Đường dẫn '{request.path}' không tồn tại hoặc đã bị xóa khỏi hệ thống."
    ), 404


@app.errorhandler(403)
def forbidden_access(error):
    # 3. Ghi log khi cố tình truy cập trái phép không có quyền
    log_security_event(f"403 Forbidden: Cố tình truy cập trái phép vào {request.path}")
    return render_template(
        'error.html',
        code=403,
        title="Không có quyền truy cập",
        message="Bạn không có quyền (vai trò admin/mod) để truy cập vào tài nguyên này."
    ), 403


if __name__ == "__main__":
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    app.run(host=host, port=port, debug=True)
