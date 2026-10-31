import unittest
from app import app
from src.models import db, User, Answer, Vote

class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_api_health_check(self):
        """Kiểm tra API test kết nối /api/test"""
        response = self.client.get('/api/test')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data.get('status'), 'success')

    def test_api_get_questions(self):
        """Kiểm tra API lấy danh sách câu hỏi /api/questions"""
        response = self.client.get('/api/questions')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data.get('status'), 'success')
        self.assertIn('data', json_data)

    def test_api_get_tags(self):
        """Kiểm tra API lấy danh sách tags /api/tags"""
        response = self.client.get('/api/tags')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data.get('status'), 'success')
        self.assertIn('data', json_data)

    def test_api_vote_answer_requires_auth(self):
        """Kiểm tra API vote câu trả lời chặn khách vãng lai (401 Unauthorized)"""
        ans = Answer.query.first()
        if ans:
            response = self.client.post(f'/api/vote/answer/{ans.id}', json={'type': 'up'})
            self.assertEqual(response.status_code, 401)
            json_data = response.get_json()
            self.assertEqual(json_data.get('status'), 'error')

    def test_api_vote_own_answer_rejected(self):
        """Kiểm tra không thể tự bình chọn cho câu trả lời của chính mình (400 Bad Request)"""
        ans = Answer.query.first()
        if not ans:
            return

        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(ans.user_id)
            sess['_fresh'] = True

        response = self.client.post(f'/api/vote/answer/{ans.id}', json={'type': 'up'})
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data.get('status'), 'error')
        self.assertIn("không thể tự bình chọn", json_data.get('message', ''))

    def test_api_vote_answer_flow(self):
        """Kiểm tra luồng vote: 1 người 1 vote, toggle hủy vote và đổi vote"""
        ans = Answer.query.first()
        if not ans:
            return

        # Tìm user không phải tác giả của câu trả lời
        other_user = User.query.filter(User.id != ans.user_id).first()
        self.assertIsNotNone(other_user, "Cần ít nhất 2 user trong cơ sở dữ liệu để test vote")

        # Xóa vote cũ của other_user đối với câu trả lời này nếu có để test sạch
        Vote.query.filter_by(user_id=other_user.id, answer_id=ans.id).delete()
        db.session.commit()

        # Đăng nhập giả lập bằng session
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(other_user.id)
            sess['_fresh'] = True

        init_upvotes = ans.upvotes or 0

        # 1. Vote Up lần đầu -> Thành công, user_vote = 1
        res1 = self.client.post(f'/api/vote/answer/{ans.id}', json={'type': 'up'})
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertEqual(data1.get('user_vote'), 1)
        self.assertEqual(data1.get('new_upvotes'), init_upvotes + 1)

        # 2. Bấm Vote Up lần thứ hai -> Hủy vote (Undo), user_vote = 0
        res2 = self.client.post(f'/api/vote/answer/{ans.id}', json={'type': 'up'})
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertEqual(data2.get('user_vote'), 0)
        self.assertEqual(data2.get('new_upvotes'), init_upvotes)

        # 3. Bấm Vote Down -> Thành công, user_vote = -1
        res3 = self.client.post(f'/api/vote/answer/{ans.id}', json={'type': 'down'})
        self.assertEqual(res3.status_code, 200)
        data3 = res3.get_json()
        self.assertEqual(data3.get('user_vote'), -1)
        self.assertEqual(data3.get('new_upvotes'), init_upvotes - 1)

        # 4. Đổi từ Down sang Up -> user_vote = 1, tăng 2 điểm
        res4 = self.client.post(f'/api/vote/answer/{ans.id}', json={'type': 'up'})
        self.assertEqual(res4.status_code, 200)
        data4 = res4.get_json()
        self.assertEqual(data4.get('user_vote'), 1)
        self.assertEqual(data4.get('new_upvotes'), init_upvotes + 1)

        # Dọn dẹp: Hủy vote để hoàn trả trạng thái ban đầu
        res_clean = self.client.post(f'/api/vote/answer/{ans.id}', json={'type': 'up'})
        self.assertEqual(res_clean.get_json().get('user_vote'), 0)

if __name__ == '__main__':
    unittest.main()

