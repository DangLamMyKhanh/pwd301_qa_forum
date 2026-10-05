from flask import Flask
from flask_wtf.csrf import CSRFProtect, CSRFError

import urllib.parse
from flask_migrate import Migrate 
from src.models import db 

app=Flask(__name__)


app.config['SECRET_KEY'] = "chuoi-bi-mat"


# CẤU HÌNH KẾT NỐI SQL SERVER (DÙNG ACC SA)
# ==========================================
# 1. Điền thông tin của em vào đây:
db_user = 'sa'
db_password = urllib.parse.quote_plus('1') # Tự động mã hóa ký tự đặc biệt
db_server = 'localhost\\SQLEXPRESS' 
db_name = 'qa_forum_db'

# 2. Tạo chuỗi kết nối
app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pyodbc://{db_user}:{db_password}@{db_server}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server'
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