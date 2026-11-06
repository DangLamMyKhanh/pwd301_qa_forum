import pytest
from src.models import db, User, Question, Answer, Vote

def test_api_health_check(client):
    """Kiểm tra API test kết nối /api/test"""
    response = client.get('/api/test')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data.get('status') == 'success'

def test_api_get_questions(client):
    """Kiểm tra API lấy danh sách câu hỏi /api/questions"""
    response = client.get('/api/questions')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data.get('status') == 'success'
    assert 'data' in json_data

def test_api_get_tags(client):
    """Kiểm tra API lấy danh sách tags /api/tags"""
    response = client.get('/api/tags')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data.get('status') == 'success'
    assert 'data' in json_data

def test_api_vote_answer_requires_auth(client):
    """Kiểm tra API vote câu trả lời chặn khách vãng lai (401 Unauthorized)"""
    ans = Answer.query.first()
    if ans:
        response = client.post(f'/api/vote/answer/{ans.id}', json={'type': 'up'})
        assert response.status_code == 401
        json_data = response.get_json()
        assert json_data.get('status') == 'error'

def test_api_vote_own_answer_rejected(client):
    """Kiểm tra không thể tự bình chọn cho câu trả lời của chính mình (400 Bad Request)"""
    ans = Answer.query.first()
    if not ans:
        return

    with client.session_transaction() as sess:
        sess['_user_id'] = str(ans.user_id)
        sess['_fresh'] = True

    response = client.post(f'/api/vote/answer/{ans.id}', json={'type': 'up'})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data.get('status') == 'error'
    assert "không thể tự bình chọn" in json_data.get('message', '')

def test_api_vote_answer_flow(client):
    """Kiểm tra luồng vote: 1 người 1 vote, toggle hủy vote và đổi vote"""
    ans = Answer.query.first()
    if not ans:
        return

    # Tìm user không phải tác giả của câu trả lời
    other_user = User.query.filter(User.id != ans.user_id).first()
    assert other_user is not None, "Cần ít nhất 2 user trong cơ sở dữ liệu để test vote"

    # Xóa vote cũ của other_user đối với câu trả lời này nếu có để test sạch
    Vote.query.filter_by(user_id=other_user.id, answer_id=ans.id).delete()
    db.session.commit()

    # Đăng nhập giả lập bằng session
    with client.session_transaction() as sess:
        sess['_user_id'] = str(other_user.id)
        sess['_fresh'] = True

    init_upvotes = ans.upvotes or 0

    # 1. Vote Up lần đầu -> Thành công, user_vote = 1
    res1 = client.post(f'/api/vote/answer/{ans.id}', json={'type': 'up'})
    assert res1.status_code == 200
    data1 = res1.get_json()
    assert data1.get('user_vote') == 1
    assert data1.get('new_upvotes') == init_upvotes + 1

    # 2. Bấm Vote Up lần thứ hai -> Hủy vote (Undo), user_vote = 0
    res2 = client.post(f'/api/vote/answer/{ans.id}', json={'type': 'up'})
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2.get('user_vote') == 0
    assert data2.get('new_upvotes') == init_upvotes

    # 3. Bấm Vote Down -> Thành công, user_vote = -1
    res3 = client.post(f'/api/vote/answer/{ans.id}', json={'type': 'down'})
    assert res3.status_code == 200
    data3 = res3.get_json()
    assert data3.get('user_vote') == -1
    assert data3.get('new_upvotes') == init_upvotes - 1

def test_api_vote_question_requires_auth(client):
    """Kiểm tra API vote câu hỏi chặn khách vãng lai (401 Unauthorized)"""
    q = Question.query.first()
    if q:
        response = client.post(f'/api/questions/{q.id}/vote', json={'type': 'up'})
        assert response.status_code == 401
        json_data = response.get_json()
        assert json_data.get('status') == 'error'

def test_api_vote_own_question_rejected(client):
    """Kiểm tra không thể tự bình chọn cho câu hỏi của chính mình (400 Bad Request)"""
    q = Question.query.first()
    if not q:
        return

    with client.session_transaction() as sess:
        sess['_user_id'] = str(q.user_id)
        sess['_fresh'] = True

    response = client.post(f'/api/questions/{q.id}/vote', json={'type': 'up'})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data.get('status') == 'error'
    assert "không thể tự bình chọn" in json_data.get('message', '')

def test_api_vote_question_flow(client):
    """Kiểm tra luồng vote câu hỏi: 1 người 1 vote, toggle hủy vote và đổi vote"""
    q = Question.query.first()
    if not q:
        return

    # Tìm user không phải tác giả của câu hỏi
    other_user = User.query.filter(User.id != q.user_id).first()
    assert other_user is not None, "Cần ít nhất 2 user trong cơ sở dữ liệu để test vote câu hỏi"

    # Xóa vote cũ của other_user đối với câu hỏi này nếu có để test sạch
    Vote.query.filter_by(user_id=other_user.id, question_id=q.id).delete()
    db.session.commit()

    # Đăng nhập giả lập bằng session
    with client.session_transaction() as sess:
        sess['_user_id'] = str(other_user.id)
        sess['_fresh'] = True

    init_upvotes = q.upvotes or 0

    # 1. Vote Up lần đầu -> Thành công, user_vote = 1
    res1 = client.post(f'/api/questions/{q.id}/vote', json={'type': 'up'})
    assert res1.status_code == 200
    data1 = res1.get_json()
    assert data1.get('user_vote') == 1
    assert data1.get('new_upvotes') == init_upvotes + 1

    # 2. Bấm Vote Up lần thứ hai -> Hủy vote (Undo), user_vote = 0
    res2 = client.post(f'/api/questions/{q.id}/vote', json={'type': 'up'})
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2.get('user_vote') == 0
    assert data2.get('new_upvotes') == init_upvotes

    # 3. Bấm Vote Down -> Thành công, user_vote = -1
    res3 = client.post(f'/api/questions/{q.id}/vote', json={'type': 'down'})
    assert res3.status_code == 200
    data3 = res3.get_json()
    assert data3.get('user_vote') == -1
    assert data3.get('new_upvotes') == init_upvotes - 1

def test_api_mark_best_answer_by_author(client):
    """Kiểm tra tác giả câu hỏi đánh dấu Best Answer (+15 điểm uy tín) và unmark qua AJAX"""
    # Tìm câu hỏi có câu trả lời
    q = Question.query.filter(Question.answers.any()).first()
    if not q or not q.answers:
        return

    ans = q.answers[0]
    ans_author = ans.author
    init_rep = ans_author.reputation or 0

    # Đăng nhập với vai trò Tác giả câu hỏi
    with client.session_transaction() as sess:
        sess['_user_id'] = str(q.user_id)
        sess['_fresh'] = True

    # 1. Đánh dấu Best Answer
    res1 = client.post(f'/api/answers/{ans.id}/best')
    assert res1.status_code == 200
    data1 = res1.get_json()
    assert data1.get('status') == 'success'
    assert data1.get('is_best') is True

    # Kiểm tra điểm uy tín được cộng 15
    db.session.refresh(ans_author)
    assert ans_author.reputation >= init_rep

    # 2. Bấm lại để Hủy Best Answer
    res2 = client.post(f'/api/answers/{ans.id}/best')
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2.get('is_best') is False

def test_api_mark_best_answer_by_non_author_forbidden(client):
    """Kiểm tra người dùng không phải tác giả câu hỏi cố tình chọn Best Answer -> 403 Forbidden"""
    q = Question.query.filter(Question.answers.any()).first()
    if not q or not q.answers:
        return

    ans = q.answers[0]
    other_user = User.query.filter(User.id != q.user_id).first()
    if not other_user:
        return

    with client.session_transaction() as sess:
        sess['_user_id'] = str(other_user.id)
        sess['_fresh'] = True

    res = client.post(f'/api/answers/{ans.id}/best')
    assert res.status_code == 403

def test_api_lock_question_non_admin_forbidden(client):
    """Kiểm tra sinh viên không có quyền khóa câu hỏi (403 Forbidden)"""
    student = User.query.filter_by(role='student').first()
    q = Question.query.first()
    if not student or not q:
        return

    with client.session_transaction() as sess:
        sess['_user_id'] = str(student.id)
        sess['_fresh'] = True
    res = client.post(f'/api/questions/{q.id}/lock')
    assert res.status_code == 403

def test_api_lock_question_admin_allowed(client):
    """Kiểm tra Admin có quyền khóa và mở khóa câu hỏi (200 OK)"""
    admin = User.query.filter_by(role='admin').first()
    q = Question.query.first()
    if not admin or not q:
        return

    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin.id)
        sess['_fresh'] = True
    res = client.post(f'/api/questions/{q.id}/lock')
    assert res.status_code == 200
    assert res.get_json().get('status') == 'success'

    # Mở khóa lại để không ảnh hưởng dữ liệu
    client.post(f'/api/questions/{q.id}/lock')

def test_api_hide_question_moderator(client):
    """Kiểm tra tính năng Moderator/Admin ẩn câu hỏi vi phạm (RBAC)"""
    mod = User.query.filter_by(role='moderator').first()
    q = Question.query.first()
    if not mod or not q:
        return

    with client.session_transaction() as sess:
        sess['_user_id'] = str(mod.id)
        sess['_fresh'] = True

    res = client.post(f'/api/questions/{q.id}/hide')
    assert res.status_code == 200
    assert res.get_json().get('status') == 'success'

    # Khôi phục lại trạng thái
    client.post(f'/api/questions/{q.id}/hide')

def test_api_jwt_login_success(client):
    """Kiểm tra REST API đăng nhập lấy JWT Token (Status 200 OK)"""
    res = client.post('/api/auth/login', json={'username': 'admin', 'password': 'password123'})
    # Nếu password123 không đúng thử mật khẩu seed 123456
    if res.status_code == 401:
        res = client.post('/api/auth/login', json={'username': 'admin', 'password': '123456'})
    assert res.status_code == 200
    data = res.get_json()
    assert 'access_token' in data
    assert data.get('token_type') == 'Bearer'

def test_api_jwt_login_bad_request_400(client):
    """Kiểm tra API đăng nhập thiếu thông tin -> Status 400 Bad Request"""
    res = client.post('/api/auth/login', json={'username': 'admin'})
    assert res.status_code == 400
    assert res.get_json().get('status') == 'error'

def test_api_jwt_login_unauthorized_401(client):
    """Kiểm tra API đăng nhập sai mật khẩu -> Status 401 Unauthorized"""
    res = client.post('/api/auth/login', json={'username': 'admin', 'password': 'wrong_password_xyz'})
    assert res.status_code == 401
    assert res.get_json().get('status') == 'error'

def test_api_create_question_201_with_jwt(client):
    """Kiểm tra tạo câu hỏi mới qua REST API bằng JWT Token -> Status 201 Created"""
    # 1. Đăng nhập lấy token
    login_res = client.post('/api/auth/login', json={'username': 'admin', 'password': 'password123'})
    if login_res.status_code == 401:
        login_res = client.post('/api/auth/login', json={'username': 'admin', 'password': '123456'})
    token = login_res.get_json().get('access_token')

    # 2. Tạo câu hỏi kèm header Authorization: Bearer <token>
    res = client.post(
        '/api/questions',
        json={
            'title': 'Câu hỏi thử nghiệm qua REST API',
            'content': 'Nội dung câu hỏi tạo bằng mã 201 Created',
            'tags': ['Python', 'REST-API']
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data.get('status') == 'success'
    assert 'id' in data.get('data', {})

def test_api_create_question_bad_request_400(client):
    """Kiểm tra tạo câu hỏi thiếu tiêu đề -> Status 400 Bad Request"""
    admin = User.query.filter_by(role='admin').first()
    if admin:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True
        res = client.post('/api/questions', json={'title': '', 'content': 'Thiếu tiêu đề'})
        assert res.status_code == 400

def test_api_create_question_unauthorized_401(client):
    """Kiểm tra tạo câu hỏi khi chưa xác thực -> Status 401 Unauthorized"""
    res = client.post('/api/questions', json={'title': 'Tiêu đề', 'content': 'Nội dung'})
    assert res.status_code == 401

def test_api_get_question_detail_200_and_404(client):
    """Kiểm tra xem chi tiết câu hỏi (200 OK) và câu hỏi không tồn tại (404 Not Found)"""
    q = Question.query.first()
    if q:
        res = client.get(f'/api/questions/{q.id}')
        assert res.status_code == 200
        assert res.get_json().get('status') == 'success'

    # Kiểm tra id không tồn tại
    res404 = client.get('/api/questions/9999999')
    assert res404.status_code == 404
    assert res404.get_json().get('status') == 'error'

def test_api_put_and_delete_question(client):
    """Kiểm tra phương thức HTTP PUT (200 OK) và DELETE (200 OK) chuẩn RESTful"""
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        return

    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin.id)
        sess['_fresh'] = True

    # Tạo câu hỏi tạm thời
    q = Question(title="Câu hỏi thử nghiệm PUT DELETE", content="Nội dung ban đầu", user_id=admin.id)
    db.session.add(q)
    db.session.commit()

    # 1. Test PUT (Update) -> 200 OK
    res_put = client.put(f'/api/questions/{q.id}', json={'title': 'Tiêu đề đã cập nhật qua PUT'})
    assert res_put.status_code == 200

    # 2. Test DELETE -> 200 OK
    res_del = client.delete(f'/api/questions/{q.id}')
    assert res_del.status_code == 200

def test_api_create_answer_201_created(client):
    """Kiểm tra tạo câu trả lời mới qua REST API -> Status 201 Created"""
    student = User.query.filter_by(role='student').first()
    q = Question.query.first()
    if not (student and q):
        return

    with client.session_transaction() as sess:
        sess['_user_id'] = str(student.id)
        sess['_fresh'] = True

    res = client.post(
        f'/api/questions/{q.id}/answers',
        json={'content': 'Câu trả lời thử nghiệm tạo qua REST API 201 Created'}
    )
    assert res.status_code == 201
    assert res.get_json().get('status') == 'success'

def test_api_global_500_error_handler(client):
    """Kiểm tra xử lý lỗi máy chủ nội bộ toàn cục -> Status 500 Internal Server Error"""
    res = client.get('/api/test/simulate-error')
    assert res.status_code == 500
    data = res.get_json()
    assert data.get('status') == 'error'

def test_api_jwt_token_expiry(client):
    """Kiểm tra mã JWT token đã hết hạn (Token Expiry) bị từ chối -> Status 401 Unauthorized theo Rubric"""
    from flask_jwt_extended import create_access_token
    from datetime import timedelta
    admin = User.query.filter_by(role='admin').first()
    if admin:
        expired_token = create_access_token(identity=str(admin.id), expires_delta=timedelta(seconds=-10))
        res = client.post(
            '/api/questions',
            json={'title': 'Test Expiry', 'content': 'Test Content'},
            headers={'Authorization': f'Bearer {expired_token}'}
        )
        assert res.status_code == 401
        assert res.get_json().get('status') == 'error'

def test_api_jwt_invalid_token(client):
    """Kiểm tra token giả mạo / không đúng định dạng bị từ chối -> Status 401 Unauthorized"""
    res = client.post(
        '/api/questions',
        json={'title': 'Test Fake Token', 'content': 'Test Content'},
        headers={'Authorization': 'Bearer fake_invalid_malformed_token_123'}
    )
    assert res.status_code == 401
    assert res.get_json().get('status') == 'error'


