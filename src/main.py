from flask import Blueprint, render_template

# Khởi tạo Blueprint có tên là 'main'
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template("index.html")