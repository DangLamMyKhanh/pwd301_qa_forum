import pytest
from src.models import db, User, Question, Answer, Tag, Permission, ROLE_PERMISSIONS
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

def test_rbac_permission_matrix(app_ctx):
    """Kiểm tra ma trận phân quyền (Role-Permission Matrix) theo Rubric Criteria 6"""
    student = User(username="student_tester", email="s@test.com", password_hash="hash", role="student")
    moderator = User(username="mod_tester", email="m@test.com", password_hash="hash", role="moderator")
    admin = User(username="admin_tester", email="a@test.com", password_hash="hash", role="admin")

    # Sinh viên: Được phép hỏi, trả lời, vote, đánh dấu câu trả lời hay nhất của mình
    assert student.can(Permission.ASK_QUESTION) is True
    assert student.can(Permission.ANSWER) is True
    assert student.can(Permission.VOTE) is True
    assert student.can(Permission.MARK_BEST_ANSWER) is True
    # Sinh viên: KHÔNG có quyền ẩn bài, khóa bài, xóa bài người khác, xem audit log
    assert student.can(Permission.HIDE_VIOLATIONS) is False
    assert student.can(Permission.LOCK_POST) is False
    assert student.can(Permission.DELETE_POST) is False
    assert student.can(Permission.VIEW_AUDIT_LOG) is False

    # Moderator: Được phép ẩn nội dung vi phạm
    assert moderator.can(Permission.HIDE_VIOLATIONS) is True
    # Moderator: KHÔNG có quyền khóa bài, xóa bài của người khác, xem audit log (Admin only)
    assert moderator.can(Permission.LOCK_POST) is False
    assert moderator.can(Permission.DELETE_POST) is False
    assert moderator.can(Permission.VIEW_AUDIT_LOG) is False

    # Admin: Toàn quyền trong hệ thống
    assert admin.can(Permission.HIDE_VIOLATIONS) is True
    assert admin.can(Permission.LOCK_POST) is True
    assert admin.can(Permission.DELETE_POST) is True
    assert admin.can(Permission.VIEW_AUDIT_LOG) is True

