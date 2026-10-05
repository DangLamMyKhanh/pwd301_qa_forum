from flask import Blueprint

# Khởi tạo Blueprint có tên là 'auth'
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    return "<h1>Đây là trang Đăng Nhập (Auth Blueprint)</h1>"

@auth_bp.route('/register')
def register():
    return "<h1>Đây là trang Đăng Ký (Auth Blueprint)</h1>"