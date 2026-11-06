import pytest
from src.models import db, User, Question, Answer, Tag
from werkzeug.security import generate_password_hash, check_password_hash

def test_user_password_hashing(app_ctx):
    """Kiểm tra mã hóa mật khẩu bằng werkzeug.security"""
    raw_password = "secure_password_123"
    hashed = generate_password_hash(raw_password)
    
    assert raw_password != hashed
    assert check_password_hash(hashed, raw_password)
    assert not check_password_hash(hashed, "wrong_password")

def test_question_and_tag_relationship(app_ctx):
    """Kiểm tra quan hệ Many-to-Many giữa Question và Tag"""
    q = Question(title="Làm sao để học Flask?", content="Nội dung câu hỏi...")
    t1 = Tag(name="Python")
    t2 = Tag(name="Flask")
    
    q.tags.append(t1)
    q.tags.append(t2)
    
    assert len(q.tags) == 2
    assert t1 in q.tags
    assert t2 in q.tags
