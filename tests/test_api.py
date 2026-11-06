import pytest
from src.models import db, User, Answer, Vote

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
