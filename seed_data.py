"""
seed_data.py - Sinh dữ liệu mẫu (seed data) cho Student Q&A Forum bằng Faker.

Cài thư viện:  pip install Faker
Chạy thử:      python seed_data.py

File này tích hợp trực tiếp với Model và Database.
Khi chạy sẽ tạo dữ liệu mẫu và lưu vào DB thật.
"""

import random

# ---------------------------------------------------------------------------
# Task 2.1: Khởi tạo Faker
# ---------------------------------------------------------------------------
from faker import Faker
from werkzeug.security import generate_password_hash

from app import app
from src.models import db, User, Question, Answer, Tag

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
    """Tạo 15 tài khoản User ảo, mật khẩu mặc định cho tất cả là '123456'."""
    users = []
    for _ in range(NUM_USERS):
        user = User(
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            password_hash=generate_password_hash(DEFAULT_PASSWORD),
        )
        db.session.add(user)
        users.append(user)
    db.session.flush()  # Gán id cho các user trước khi dùng ở bước sau
    return users


def create_tags():
    """Tạo list tag cố định: Python, Flask, Bug, Database, Frontend."""
    tags = []
    for name in TAG_NAMES:
        tag = Tag(name=name)
        db.session.add(tag)
        tags.append(tag)
    db.session.flush()  # Gán id cho các tag
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
        )
        db.session.add(a)
        answers.append(a)
    return answers


# ---------------------------------------------------------------------------
# Chạy thử: python seed_data.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        users = create_users()
        tags = create_tags()
        questions = create_questions(users, tags)
        answers = create_answers(users, questions)
        db.session.commit()

        print(f"=== {len(users)} USER ===")
        for u in users:
            print(f"- {u.username} | {u.email} | mật khẩu: {DEFAULT_PASSWORD}")

        print(f"\n=== TAG: {', '.join(t.name for t in tags)} ===")

        print(f"\n=== {len(questions)} CÂU HỎI ===")
        for i, q in enumerate(questions, start=1):
            tag_names = ', '.join(t.name for t in q.tags)
            print(f"[{i}] {q.title}  (tác giả: {q.author.username}, nhãn: {tag_names})")

        print(f"\n=== {len(answers)} CÂU TRẢ LỜI ===")
        for a in answers[:5]:
            print(f"- {a.author.username} trả lời '{a.question.title}': {a.content}")
        print("...")

        print(f"\n✅ Đã seed thành công: {len(users)} users, {len(tags)} tags, "
              f"{len(questions)} questions, {len(answers)} answers")