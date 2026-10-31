import unittest
from app import app
from src.models import User

class RouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_homepage_loads(self):
        """Kiểm tra trang chủ tải thành công 200"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Student Q&A Forum", response.data)

    def test_homepage_sort_by_votes(self):
        """Kiểm tra trang chủ lọc sắp xếp theo số vote /?sort=votes tải thành công 200"""
        response = self.client.get('/?sort=votes')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Nhiều vote nhất".encode('utf-8'), response.data)

    def test_login_page_loads(self):
        """Kiểm tra trang đăng nhập tải thành công 200"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"csrf_token", response.data)

    def test_register_page_loads(self):
        """Kiểm tra trang đăng ký tải thành công 200"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"csrf_token", response.data)

    def test_ask_question_requires_login(self):
        """Kiểm tra trang đặt câu hỏi bắt buộc đăng nhập (Redirect 302 -> /login)"""
        response = self.client.get('/ask')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers.get('Location', ''))

    def test_user_profile_page_loads(self):
        """Kiểm tra xem hồ sơ của một thành viên bất kỳ (/user/<id>)"""
        user = User.query.first()
        if user:
            response = self.client.get(f'/user/{user.id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn(user.username.encode('utf-8'), response.data)

    def test_404_not_found(self):
        """Kiểm tra xử lý lỗi 404 cho route không tồn tại"""
        response = self.client.get('/duong-dan-khong-ton-tai-123')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"404", response.data)

    def test_rbac_moderator_user_exists(self):
        """Kiểm tra tài khoản Moderator đã tồn tại trong hệ thống RBAC"""
        mod = User.query.filter_by(username='moderator').first()
        self.assertIsNotNone(mod)
        self.assertEqual(mod.role, 'moderator')

    def test_idor_unauthorized_user_cannot_delete_question(self):
        """Kiểm tra chống lỗi IDOR: Sinh viên không được xóa câu hỏi của người khác (403)"""
        import re
        from src.models import Question
        q = Question.query.first()
        if q:
            # Tìm student không phải là tác giả của câu hỏi
            other_student = User.query.filter(User.id != q.user_id, User.role == 'student').first()
            if other_student:
                with self.client.session_transaction() as sess:
                    sess['_user_id'] = str(other_student.id)
                    sess['_fresh'] = True
                
                # Lấy trang chủ để trích xuất CSRF token từ thẻ meta
                res_page = self.client.get('/')
                match = re.search(r'<meta name="csrf-token" content="([^"]+)">', res_page.get_data(as_text=True))
                csrf_tok = match.group(1) if match else ''

                # Cố tình gọi xóa câu hỏi của người khác -> Bị từ chối 403 Forbidden
                res = self.client.post(f'/question/{q.id}/delete', headers={'X-CSRFToken': csrf_tok})
                self.assertEqual(res.status_code, 403)

if __name__ == '__main__':
    unittest.main()
