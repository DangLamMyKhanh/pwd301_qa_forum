import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.engine import URL

# Nạp các biến môi trường từ file .env
load_dotenv(Path(__file__).resolve().parent / '.env')


class Config:
    """Cấu hình cơ bản cho ứng dụng Flask Student Q&A Forum"""

    # 1. Khóa bảo mật Session & JWT Token
    SECRET_KEY = os.getenv('SECRET_KEY', 'pwd301-qa-forum-flask-secret-key-2026')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'pwd301-qa-forum-jwt-access-secret-2026')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1) # Cấu hình thời hạn hết hạn JWT Token (Token Expiry)

    # 2. Cấu hình Session an toàn (HttpOnly, Secure, Reasonable Timeout)
    SESSION_COOKIE_HTTPONLY = True              # Chống XSS đọc trộm cookie session từ JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'             # Chống tấn công CSRF điều hướng chéo domain
    SESSION_COOKIE_SECURE = False               # Mặc định False để chạy được trên localhost HTTP
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2) # Timeout phiên đăng nhập hợp lý: 2 giờ

    # Cấu hình Remember Me an toàn
    REMEMBER_COOKIE_HTTPONLY = True             # Chống JavaScript truy cập remember cookie
    REMEMBER_COOKIE_DURATION = timedelta(days=14) # Ghi nhớ đăng nhập trong 14 ngày
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    # 3. Cấu hình chuỗi kết nối SQL Server (dùng driver pymssql qua TCP/IP)
    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="mssql+pymssql",
        username=os.getenv("DB_USER", "sa"),
        password=os.getenv("DB_PASSWORD", "1"),
        host=os.getenv("DB_SERVER", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 1433)),
        database=os.getenv("DB_NAME", "qa_forum_db"),
        query={'charset': 'UTF-8'}
    )

    # 3. Tắt thông báo theo dõi thay đổi của Flask-SQLAlchemy để tối ưu tài nguyên
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 4. Tối ưu hóa Connection Pool và Timeout cho kết nối cơ sở dữ liệu
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Kiểm tra kết nối trong pool trước khi sử dụng
        "connect_args": {
            'charset': 'UTF-8',
            'login_timeout': 5,
            'timeout': 10
        },
    }

    # 5. Giới hạn dung lượng tải lên (Upload limit: 64 KB cho text/form)
    MAX_CONTENT_LENGTH = 64 * 1024

    # 6. Cấu hình phân trang (Pagination Settings)
    POSTS_PER_PAGE = int(os.getenv('POSTS_PER_PAGE', 20))
    LOGS_PER_PAGE = int(os.getenv('LOGS_PER_PAGE', 20))


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True                # Bắt buộc chỉ gửi qua giao thức HTTPS trên môi trường Production
    REMEMBER_COOKIE_SECURE = True

