from flask import Blueprint, request, redirect, url_for, flash, abort, render_template
from flask_login import login_user, logout_user, login_required, current_user
from src.models import db, User
from src.extensions import bcrypt
from functools import wraps

from src.forms import LoginForm, RegistrationForm, QuestionForm, AnswerForm

from flask_jwt_extended import create_access_token


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

    form = RegistrationForm()

    if form.validate_on_submit():
        # Kiểm tra trùng lặp username hoặc email
        if User.query.filter_by(username=form.username.data).first():
            flash('Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác!', 'danger')
            return render_template('register.html', form=form)
            
        if User.query.filter_by(email=form.email.data).first():
            flash('Email này đã được đăng ký tài khoản rồi!', 'danger')
            return render_template('register.html', form=form)

        # 1. Băm cái mật khẩu thành chuỗi bí mật
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # 2. Tạo đối tượng User mới với dữ liệu từ Form
        user_moi = User(
            username=form.username.data, 
            email=form.email.data, 
            password_hash=hashed_password
        )
        
        # 3. Lưu vào Database
        db.session.add(user_moi)
        db.session.commit()
        
        # 4. Báo cáo thành công và đá sang trang Đăng nhập
        flash('Tạo tài khoản thành công! Đăng nhập ngay nào.', 'success')
        return redirect(url_for('auth.login'))

    # NẾU LÀ TRUY CẬP BÌNH THƯỜNG (GET) HOẶC FORM BỊ LỖI KHI BẤM (POST)
    # Thì hiển thị lại cái form cho người ta nhập lại
    return render_template('register.html', form=form)
   


# ==========================================
# 3. LOGIC ĐĂNG NHẬP (KIỂM TRA HASH)
# ==========================================
@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # THAY ĐỔI 1: Hàm này sẽ tự động check phương thức POST + check CSRF Token + check Validator của Thành viên 2
    if form.validate_on_submit(): 
        
        # THAY ĐỔI 2: Rút dữ liệu TỪ TRONG CÁI FORM ra, không dùng request.form.get nữa
        email = form.email.data
        password = form.password.data
        
        user = User.query.filter_by(email=email).first()

        # Nếu có user và mật khẩu sau khi giải băm khớp nhau
        if user and bcrypt.check_password_hash(user.password_hash, password):
            # 1. Cấp session duyệt web (Cũ)
            login_user(user) 
            
            # 2. TẠO CHÌA KHÓA JWT TOKEN (MỚI THÊM)
            # Tạo 1 token có chứa ID của user, dùng để gọi API
            access_token = create_access_token(identity=str(user.id))
            
            flash('Đăng nhập thành công!', 'success')
            
            # 3. Truyền cái Token này sang trang Chủ cho JS xài
            return render_template('index.html', jwt_token=access_token)
        else:
            flash('Email hoặc mật khẩu không đúng!', 'danger')
            # TODO: Sau này chèn hàm Ghi Log (Sai mật khẩu) vào đây
            
    # Nếu là GET hoặc form bị lỗi validator thì load lại trang
    return render_template("login.html", form=form)


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