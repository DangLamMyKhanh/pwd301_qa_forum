from flask import Blueprint, request, redirect, url_for, flash, abort, render_template, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.models import db, User, SecurityAuditLog
from functools import wraps

from src.forms import LoginForm, RegistrationForm, QuestionForm, AnswerForm
from flask_jwt_extended import create_access_token


# Khởi tạo Blueprint có tên là 'auth'
auth_bp = Blueprint('auth', __name__)

# ==========================================
# HÀM HỖ TRỢ GHI AUDIT LOG
# ==========================================
def log_audit(action, user_id=None):
    """Ghi nhận sự kiện xác thực và an ninh vào SecurityAuditLog"""
    try:
        ip_addr = request.remote_addr or 'Unknown'
        uid = user_id or (current_user.id if current_user.is_authenticated else None)
        log = SecurityAuditLog(user_id=uid, ip_address=ip_addr, action=action)
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[AUDIT LOG ERROR]: {e}")


# ==========================================
# 1. BẢO MẬT: CUSTOM DECORATOR (RBAC)
# ==========================================
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Chưa đăng nhập -> Về trang login
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            # Sai quyền -> ghi log nỗ lực trái phép và trả về 403
            if current_user.role not in roles:
                log_audit(f"Nỗ lực truy cập trái phép: User '{current_user.username}' (role: {current_user.role}) cố tình vào trang yêu cầu quyền {roles}")
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator



# ==========================================
# 2. LOGIC ĐĂNG KÝ (CÓ BĂM MẬT KHẨU & GHI LOG XÁC THỰC)
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

        # 1. Băm mật khẩu bằng Werkzeug
        hashed_password = generate_password_hash(form.password.data)

        # 2. Tạo đối tượng User mới với dữ liệu từ Form
        user_moi = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            role='student'
        )

        # 3. Lưu vào Database
        db.session.add(user_moi)
        db.session.commit()

        # 4. Ghi Audit Log sự kiện xác thực: Đăng ký tài khoản mới
        log_audit(f"Sự kiện xác thực: Đăng ký tài khoản mới thành công (User: {user_moi.username})", user_id=user_moi.id)

        # 5. Báo cáo thành công và chuyển sang trang Đăng nhập
        flash('Tạo tài khoản thành công! Đăng nhập ngay nào.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)



# ==========================================
# 3. LOGIC ĐĂNG NHẬP (KIỂM TRA HASH & GHI LOG THÀNH CÔNG / THẤT BẠI)
# ==========================================
@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        # Nếu có user và mật khẩu sau khi giải băm khớp nhau (dùng Werkzeug)
        if user and check_password_hash(user.password_hash, password):
            # 1. Cấp session duyệt web
            login_user(user)

            # 2. TẠO CHÌA KHÓA JWT TOKEN (Cho API/AJAX)
            access_token = create_access_token(identity=str(user.id))
            session['jwt_token'] = access_token

            # 3. Ghi Audit Log sự kiện xác thực: Đăng nhập thành công
            log_audit(f"Sự kiện xác thực: Đăng nhập thành công (User: {user.username})", user_id=user.id)

            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('main.index'))
        else:
            # 4. Ghi Audit Log nỗ lực truy cập trái phép / sai mật khẩu
            log_audit(f"Nỗ lực truy cập trái phép: Đăng nhập thất bại (Email: '{email}')")
            flash('Email hoặc mật khẩu không đúng!', 'danger')

    return render_template("login.html", form=form)


# ==========================================
# 4. LOGIC ĐĂNG XUẤT (GHI LOG)
# ==========================================
@auth_bp.route('/logout')
@login_required
def logout():
    uname = current_user.username
    uid = current_user.id
    logout_user()
    session.pop('jwt_token', None)

    # Ghi Audit Log sự kiện xác thực: Đăng xuất
    log_audit(f"Sự kiện xác thực: Người dùng đăng xuất khỏi hệ thống (User: {uname})", user_id=uid)

    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('auth.login'))


# ==========================================
# 5. KHU VỰC QUẢN TRỊ VIÊN & XEM LOG BẢO MẬT (PHÂN TRANG 20 LOG/TRANG)
# ==========================================
@auth_bp.route('/admin-only')
@role_required('admin')
def admin_dashboard():
    page = request.args.get('page', 1, type=int)

    # Thống kê tổng thể trên toàn bộ cơ sở dữ liệu logs
    all_logs = SecurityAuditLog.query.all()
    total_logs = len(all_logs)
    csrf_count = sum(1 for l in all_logs if 'CSRF' in (l.action or ''))
    spam_count = sum(1 for l in all_logs if 'Spam' in (l.action or ''))
    auth_fail_count = sum(1 for l in all_logs if ('thất bại' in (l.action or '') or 'Nỗ lực' in (l.action or '')))
    error_count = sum(1 for l in all_logs if ('403' in (l.action or '') or '404' in (l.action or '')))

    # Phân trang: lấy số lượng từ cấu hình LOGS_PER_PAGE trong config.py
    per_page = current_app.config.get('LOGS_PER_PAGE', 20)
    pagination = SecurityAuditLog.query.order_by(SecurityAuditLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    logs = pagination.items
    all_users = User.query.all()
    users_map = {u.id: u.username for u in all_users}

    return render_template(
        'admin_logs.html',
        logs=logs,
        pagination=pagination,
        users_map=users_map,
        total_logs=total_logs,
        csrf_count=csrf_count,
        spam_count=spam_count,
        auth_fail_count=auth_fail_count,
        error_count=error_count
    )


# ==========================================
# 6. TRANG HỒ SƠ CÁ NHÂN & THÔNG TIN USER (PROFILE)
# ==========================================
@auth_bp.route('/profile')
@login_required
def profile():
    """Trang xem hồ sơ cá nhân của chính người dùng đang đăng nhập"""
    return redirect(url_for('auth.user_profile', user_id=current_user.id))


@auth_bp.route('/user/<int:user_id>')
def user_profile(user_id):
    """Trang xem chi tiết tài khoản của bất kỳ thành viên nào trên diễn đàn"""
    user = User.query.get_or_404(user_id)

    # Sắp xếp câu hỏi và câu trả lời mới nhất lên đầu
    user_questions = sorted(user.questions, key=lambda q: q.created_at, reverse=True)
    user_answers = sorted(user.answers, key=lambda a: a.created_at, reverse=True)
    total_votes = sum((a.upvotes or 0) for a in user.answers)

    is_own_profile = current_user.is_authenticated and current_user.id == user.id

    return render_template(
        'profile.html',
        profile_user=user,
        questions=user_questions,
        answers=user_answers,
        total_votes=total_votes,
        is_own_profile=is_own_profile
    )
