from flask import Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from src.models import db, User
from src.extensions import bcrypt
from functools import wraps

# Khởi tạo Blueprint có tên là 'auth'
auth_bp = Blueprint('auth', __name__)

# ==========================================
# 1. BẢO MẬT: CUSTOM DECORATOR (RBAC)
# ==========================================
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Chưa đăng nhập -> Đá ra trang login
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            # Sai quyền -> ra lỗi 403 (Global Error Handler sẽ bắt và ghi log)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator



# ==========================================
# 2. LOGIC ĐĂNG KÝ (CÓ BĂM MẬT KHẨU)
# ==========================================
@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    # TODO:
    # Sau sẽ import Form của An 
    # from src.forms import RegistrationForm
    # form = RegistrationForm()
    # if form.validate_on_submit():
    pass


# ==========================================
# 3. LOGIC ĐĂNG NHẬP (KIỂM TRA HASH)
# ==========================================
@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()

        # Nếu có user và mật khẩu sau khi giải băm khớp nhau
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user) # Cấp session đăng nhập
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Email hoặc mật khẩu không đúng!', 'danger')
            # TODO: Sau này chèn hàm Ghi Log (Sai mật khẩu) vào đây
            
    return "Gọi giao diện html Login"


# ==========================================
# 4. LOGIC ĐĂNG XUẤT
# ==========================================
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('auth.login'))


# ==========================================
# 5. KHU VỰC TEST PHÂN QUYỀN (CHỈ DÀNH CHO ADMIN)
# ==========================================
@auth_bp.route('/admin-only')
@role_required('admin') 
def admin_dashboard():
    return "<h1>Chào Admin.</h1>"