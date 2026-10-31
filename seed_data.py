"""
seed_data.py - Sinh dữ liệu mẫu (seed data) cho Student Q&A Forum bằng Faker.

Cài thư viện:  pip install Faker
Chạy thử:      python seed_data.py

File này tích hợp trực tiếp với Model và Database.
Khi chạy sẽ tạo dữ liệu mẫu và lưu vào DB thật.
"""

import random
from faker import Faker

from app import app
from src.models import db, User, Question, Answer, Tag
from werkzeug.security import generate_password_hash

fake = Faker()

# Số lượng dữ liệu cần sinh (theo yêu cầu)
NUM_USERS = 15
NUM_QUESTIONS = 30
NUM_ANSWERS = 60
DEFAULT_PASSWORD = "123456"
TAG_NAMES = ["Python", "Flask", "Bug", "Database", "Frontend"]


# ---------------------------------------------------------------------------
# Task 2.2: Các hàm tạo dữ liệu
# ---------------------------------------------------------------------------
def create_users():
    """Tạo 15 tài khoản User ảo và 1 tài khoản Admin, mật khẩu mặc định là '123456' (dùng Werkzeug)."""
    users = []
    hashed_pw = generate_password_hash(DEFAULT_PASSWORD)

    # 1. Tạo hoặc cập nhật tài khoản Admin (Role: admin) để xem Log và kiểm tra phân quyền
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@student.edu.vn",
            password_hash=hashed_pw,
            role="admin"
        )
        db.session.add(admin)
    else:
        admin.password_hash = hashed_pw
        admin.role = "admin"
    users.append(admin)

    # 2. Tạo hoặc cập nhật tài khoản Moderator (Role: moderator) để kiểm duyệt nội dung
    mod = User.query.filter_by(username="moderator").first()
    if not mod:
        mod = User(
            username="moderator",
            email="moderator@student.edu.vn",
            password_hash=hashed_pw,
            role="moderator"
        )
        db.session.add(mod)
    else:
        mod.password_hash = hashed_pw
        mod.role = "moderator"
    users.append(mod)

    # Cập nhật mật khẩu Werkzeug cho toàn bộ user hiện có trong DB
    existing_users = User.query.all()
    for u in existing_users:
        u.password_hash = hashed_pw

    # 3. Tạo 15 User học sinh thông thường
    for _ in range(NUM_USERS):
        user = User(
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            password_hash=hashed_pw,
            role="student"
        )
        db.session.add(user)
        users.append(user)

    db.session.flush()  # Gán id cho các user trước khi dùng ở bước sau
    return users


def create_tags():
    """Tạo list tag cố định: Python, Flask, Bug, Database, Frontend."""
    tags = []
    for name in TAG_NAMES:
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
            db.session.flush()
        tags.append(tag)
    return tags


def create_questions(users, tags):
    """Tạo 30 câu hỏi. Mỗi câu có tác giả là 1 User ngẫu nhiên và gắn 1-2 tag ngẫu nhiên."""
    questions = []
    for _ in range(NUM_QUESTIONS):
        q = Question(
            title=fake.sentence(),
            content=fake.paragraph(),
            user_id=random.choice(users).id,
        )
        q.tags = random.sample(tags, k=random.randint(1, 2))
        db.session.add(q)
        questions.append(q)
    db.session.flush()  # Gán id cho các question
    return questions


def create_answers(users, questions):
    """Tạo 60 câu trả lời. Mỗi câu thuộc về 1 User ngẫu nhiên và 1 Câu hỏi ngẫu nhiên."""
    answers = []
    for _ in range(NUM_ANSWERS):
        a = Answer(
            content=fake.paragraph(),
            user_id=random.choice(users).id,
            question_id=random.choice(questions).id,
            upvotes=random.randint(0, 25)
        )
        db.session.add(a)
        answers.append(a)
    return answers


# ---------------------------------------------------------------------------
# Chạy thử: python seed_data.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        users = create_users()
        tags = create_tags()
        questions = create_questions(users, tags)
        answers = create_answers(users, questions)
        db.session.commit()

        print(f"=== {len(users)} USER (Admin: admin@student.edu.vn | Mod: moderator@student.edu.vn | pass: {DEFAULT_PASSWORD}) ===")
        for u in users:
            print(f"- {u.username} ({u.role}) | {u.email} | pass: {DEFAULT_PASSWORD}")

        print(f"\n=== TAG: {', '.join(t.name for t in tags)} ===")

        print(f"\n=== {len(questions)} CAU HOI ===")
        for i, q in enumerate(questions, start=1):
            tag_names = ', '.join(t.name for t in q.tags)
            print(f"[{i}] {q.title}  (tac gia: {q.author.username}, tag: {tag_names})")

        print(f"\n=== {len(answers)} CAU TRA LOI ===")
        for a in answers[:5]:
            print(f"- {a.author.username} tra loi '{a.question.title}': {a.content[:30]}...")
        print("...")

        print(f"\nDa seed thanh cong: {len(users)} users, {len(tags)} tags, "
              f"{len(questions)} questions, {len(answers)} answers")
