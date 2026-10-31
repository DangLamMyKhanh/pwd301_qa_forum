import unittest
from app import app
from src.models import db, User, Question, Answer, Tag
from werkzeug.security import generate_password_hash, check_password_hash

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_user_password_hashing(self):
        """Kiểm tra mã hóa mật khẩu bằng werkzeug.security"""
        raw_password = "secure_password_123"
        hashed = generate_password_hash(raw_password)
        
        self.assertNotEqual(raw_password, hashed)
        self.assertTrue(check_password_hash(hashed, raw_password))
        self.assertFalse(check_password_hash(hashed, "wrong_password"))

    def test_question_and_tag_relationship(self):
        """Kiểm tra quan hệ Many-to-Many giữa Question và Tag"""
        q = Question(title="Làm sao để học Flask?", content="Nội dung câu hỏi...")
        t1 = Tag(name="Python")
        t2 = Tag(name="Flask")
        
        q.tags.append(t1)
        q.tags.append(t2)
        
        self.assertEqual(len(q.tags), 2)
        self.assertIn(t1, q.tags)
        self.assertIn(t2, q.tags)

if __name__ == '__main__':
    unittest.main()

