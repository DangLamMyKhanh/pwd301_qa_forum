import re
import pytest
from src.models import User, Question

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
