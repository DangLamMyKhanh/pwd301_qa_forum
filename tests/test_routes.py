import re
import pytest
from src.models import db, User, Question, Answer

def test_homepage_loads(client):
    """Kiểm tra trang chủ tải thành công 200"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Student Q&A Forum" in response.data

def test_homepage_sort_by_votes(client):
    """Kiểm tra trang chủ lọc sắp xếp theo số vote /?sort=votes tải thành công 200"""
    response = client.get('/?sort=votes')
    assert response.status_code == 200
    assert "Nhiều vote nhất".encode('utf-8') in response.data

def test_login_page_loads(client):
    """Kiểm tra trang đăng nhập tải thành công 200"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"csrf_token" in response.data

def test_register_page_loads(client):
    """Kiểm tra trang đăng ký tải thành công 200"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b"csrf_token" in response.data

def test_csrf_protection_rejects_post_without_token(client):
    """Kiểm tra Flask-WTF chặn các POST form nếu thiếu CSRF token (400 Bad Request)"""
    response = client.post('/login', data={'email': 'test@test.com', 'password': '123'})
    assert response.status_code == 400
    assert b"CSRF" in response.data

def test_secure_session_configuration():
    """Kiểm tra cấu hình bảo mật Session theo Rubric CLO5 (HttpOnly, Lax, Timeout)"""
    from app import app
    assert app.config.get('SESSION_COOKIE_HTTPONLY') is True
    assert app.config.get('SESSION_COOKIE_SAMESITE') == 'Lax'
    assert app.config.get('PERMANENT_SESSION_LIFETIME') is not None
    assert app.config.get('REMEMBER_COOKIE_HTTPONLY') is True

def test_login_open_redirect_prevention(client):
    """Kiểm tra chống lỗi Open Redirect: không chuyển hướng sang domain ngoài độc hại"""
    res_page = client.get('/login')
    match = re.search(r'<meta name="csrf-token" content="([^"]+)">', res_page.get_data(as_text=True))
    csrf_tok = match.group(1) if match else ''

    admin = User.query.filter_by(role='admin').first()
    if admin:
        res = client.post(
            '/login?next=https://malicious-phishing.com',
            data={'email': admin.email, 'password': '123456', 'csrf_token': csrf_tok},
            headers={'X-CSRFToken': csrf_tok}
        )
        assert res.status_code == 302
        assert 'https://malicious-phishing.com' not in res.headers.get('Location', '')

def test_change_password_requires_login(client):
    """Kiểm tra trang đổi mật khẩu bắt buộc đăng nhập (Redirect 302 -> /login)"""
    res = client.get('/change-password')
    assert res.status_code == 302
    assert '/login' in res.headers.get('Location', '')

def test_ask_question_requires_login(client):
    """Kiểm tra trang đặt câu hỏi bắt buộc đăng nhập (Redirect 302 -> /login)"""
    response = client.get('/ask')
    assert response.status_code == 302
    assert '/login' in response.headers.get('Location', '')

def test_user_profile_page_loads(client):
    """Kiểm tra xem hồ sơ của một thành viên bất kỳ (/user/<id>)"""
    user = User.query.first()
    if user:
        response = client.get(f'/user/{user.id}')
        assert response.status_code == 200
        assert user.username.encode('utf-8') in response.data

def test_404_not_found(client):
    """Kiểm tra xử lý lỗi 404 cho route không tồn tại"""
    response = client.get('/duong-dan-khong-ton-tai-123')
    assert response.status_code == 404
    assert b"404" in response.data

def test_rbac_moderator_user_exists(app_ctx):
    """Kiểm tra tài khoản Moderator đã tồn tại trong hệ thống RBAC"""
    mod = User.query.filter_by(username='moderator').first()
    assert mod is not None
    assert mod.role == 'moderator'

def test_idor_unauthorized_user_cannot_delete_question(client):
    """Kiểm tra chống lỗi IDOR: Sinh viên không được xóa câu hỏi của người khác (403)"""
    q = Question.query.first()
    if q:
        # Tìm student không phải là tác giả của câu hỏi
        other_student = User.query.filter(User.id != q.user_id, User.role == 'student').first()
        if other_student:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(other_student.id)
                sess['_fresh'] = True
            
            # Lấy trang chủ để trích xuất CSRF token từ thẻ meta
            res_page = client.get('/')
            match = re.search(r'<meta name="csrf-token" content="([^"]+)">', res_page.get_data(as_text=True))
            csrf_tok = match.group(1) if match else ''

            # Cố tình gọi xóa câu hỏi của người khác -> Bị từ chối 403 Forbidden
            res = client.post(f'/question/{q.id}/delete', headers={'X-CSRFToken': csrf_tok})
            assert res.status_code == 403

def test_rbac_moderator_cannot_delete_question(client):
    """Kiểm tra RBAC: Moderator KHÔNG được xóa bài viết (chỉ Admin mới có quyền xóa) -> 403"""
    mod = User.query.filter_by(role='moderator').first()
    q = Question.query.first()
    if mod and q and q.user_id != mod.id:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(mod.id)
            sess['_fresh'] = True
        res_page = client.get('/')
        match = re.search(r'<meta name="csrf-token" content="([^"]+)">', res_page.get_data(as_text=True))
        csrf_tok = match.group(1) if match else ''

        res = client.post(f'/question/{q.id}/delete', headers={'X-CSRFToken': csrf_tok})
        assert res.status_code == 403

def test_locked_question_blocks_student_answers(client):
    """Kiểm tra câu hỏi bị khóa sẽ chặn sinh viên gửi câu trả lời"""
    q = Question.query.first()
    student = User.query.filter_by(role='student').first()
    if not q or not student:
        return

    # Khóa câu hỏi
    q.is_locked = True
    db.session.commit()

    with client.session_transaction() as sess:
        sess['_user_id'] = str(student.id)
        sess['_fresh'] = True

    # Lấy CSRF token
    res_page = client.get(f'/question/{q.id}')
    match = re.search(r'<meta name="csrf-token" content="([^"]+)">', res_page.get_data(as_text=True))
    csrf_tok = match.group(1) if match else ''

    res = client.post(
        f'/question/{q.id}/answer',
        data={'content': 'Câu trả lời thử nghiệm', 'csrf_token': csrf_tok},
        headers={'X-CSRFToken': csrf_tok}
    )
    # Bị chuyển hướng kèm thông báo cảnh báo đã khóa
    assert res.status_code == 302

    # Mở khóa lại
    q.is_locked = False
    db.session.commit()

def test_permission_required_blocks_student_from_locking(client):
    """Kiểm tra @permission_required(Permission.LOCK_POST) chặn sinh viên khóa bài (403 Forbidden)"""
    student = User.query.filter_by(role='student').first()
    q = Question.query.first()
    if student and q:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(student.id)
            sess['_fresh'] = True
        res_page = client.get('/')
        match = re.search(r'<meta name="csrf-token" content="([^"]+)">', res_page.get_data(as_text=True))
        csrf_tok = match.group(1) if match else ''

        res = client.post(f'/question/{q.id}/lock', headers={'X-CSRFToken': csrf_tok})
        assert res.status_code == 403

def test_permission_required_blocks_student_from_hiding(client):
    """Kiểm tra @permission_required(Permission.HIDE_VIOLATIONS) chặn sinh viên ẩn câu hỏi (403 Forbidden)"""
    student = User.query.filter_by(role='student').first()
    q = Question.query.first()
    if student and q:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(student.id)
            sess['_fresh'] = True
        res_page = client.get('/')
        match = re.search(r'<meta name="csrf-token" content="([^"]+)">', res_page.get_data(as_text=True))
        csrf_tok = match.group(1) if match else ''

        res = client.post(f'/question/{q.id}/hide', headers={'X-CSRFToken': csrf_tok})
        assert res.status_code == 403

def test_permission_required_allows_moderator_to_hide(client):
    """Kiểm tra @permission_required(Permission.HIDE_VIOLATIONS) cho phép Moderator ẩn câu hỏi vi phạm (302)"""
    mod = User.query.filter_by(role='moderator').first()
    q = Question.query.first()
    if mod and q:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(mod.id)
            sess['_fresh'] = True
        res_page = client.get('/')
        match = re.search(r'<meta name="csrf-token" content="([^"]+)">', res_page.get_data(as_text=True))
        csrf_tok = match.group(1) if match else ''

        res = client.post(f'/question/{q.id}/hide', headers={'X-CSRFToken': csrf_tok})
        assert res.status_code == 302

        # Khôi phục trạng thái cũ
        q.is_hidden = False
        db.session.commit()

def test_admin_dashboard_anonymous_redirect(client):
    """Kiểm tra chưa đăng nhập truy cập /admin bị redirect 302 về /login"""
    res = client.get('/admin')
    assert res.status_code == 302
    assert '/login' in res.headers.get('Location', '')

def test_admin_dashboard_student_forbidden(client):
    """Kiểm tra sinh viên truy cập /admin bị chặn 403 Forbidden bởi @role_required và @permission_required"""
    student = User.query.filter_by(role='student').first()
    if student:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(student.id)
            sess['_fresh'] = True
        res = client.get('/admin')
        assert res.status_code == 403

def test_admin_dashboard_admin_allowed(client):
    """Kiểm tra Admin truy cập /admin thành công 200 OK với đầy đủ quyền"""
    admin = User.query.filter_by(role='admin').first()
    if admin:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True
        res = client.get('/admin')
        assert res.status_code == 200
        assert "Nhật ký hoạt động hệ thống".encode('utf-8') in res.data

