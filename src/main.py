from flask import Blueprint

# Khởi tạo Blueprint có tên là 'main'
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return "<h1>Trang chủ Diễn đàn (Main Blueprint)</h1>"