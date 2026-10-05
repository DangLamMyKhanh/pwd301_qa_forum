from flask import Flask
from flask_wtf.csrf import CSRFProtect, CSRFError

import urllib.parse
import os                      
from dotenv import load_dotenv


from flask_migrate import Migrate 
from src.models import db 

app=Flask(__name__)

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


# ==========================================
# CẤU HÌNH KẾT NỐI SQL SERVER (TCP/IP - KHÔNG DÙNG ODBC)
# ==========================================
db_server = os.getenv('DB_SERVER')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = urllib.parse.quote_plus(os.getenv('DB_PASSWORD'))

# Chuỗi kết nối dùng pymssql 
app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pymssql://{db_user}:{db_password}@{db_server}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo Database và Migrate với App
db.init_app(app)
migrate = Migrate(app, db)
# ==========================================


CSRFProtect(app)

# đăng ký các blueprint
from src.auth import auth_bp
from src.api import api_bp
from src.main import main_bp
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)


@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    # TODO: ghi log database
    return "<h1>Lỗi 400: Yêu cầu không hợp lệ</h1>", 400


@app.errorhandler(404)
def not_found(error):
    # TODO: ghi log database
    return "<h1>Lỗi 404: Trang không tồn tại</h1>", 404

@app.errorhandler(403)
def forbidden_access(error):
    # TODO: ghi log database
    return "<h1>Lỗi 403: Không có quyền truy cập</h1>", 403


if __name__ =="__main__":
    app.run(debug=True)