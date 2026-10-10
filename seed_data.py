"""
seed_data.py - Sinh dữ liệu ảo (seed data) cho Student Q&A Forum bằng Faker.

File này hoàn toàn độc lập: không import app, models hay database.
Các hàm generate_* trả về list các dict thuần Python, để phụ trách
database có thể import và lưu vào DB sau này, ví dụ:

    from seed_data import generate_users, generate_questions, generate_answers
"""

import random
import re
import sys
import unicodedata

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

from faker import Faker

# Đặt SEED = 42 (hoặc số bất kỳ) nếu muốn mỗi lần chạy ra cùng một kết quả.
# Để None thì mỗi lần chạy sẽ ra dữ liệu ngẫu nhiên khác nhau.
SEED = None

fake = Faker("vi_VN")
if SEED is not None:
    Faker.seed(SEED)
    random.seed(SEED)

EMAIL_DOMAINS = ["gmail.com", "outlook.com", "student.edu.vn"]

# ---------------------------------------------------------------------------
# Kho nội dung mẫu (câu hỏi sinh viên hay gặp)
# ---------------------------------------------------------------------------
QUESTION_BANK = [
    {
        "tags": ["python", "lập trình"],
        "titles": [
            "Sự khác nhau giữa list và tuple trong Python là gì?",
            "Tại sao vòng lặp for của mình in ra kết quả bị lặp lại?",
            "Làm sao để đọc dữ liệu từ file CSV bằng Python?",
        ],
    },
    {
        "tags": ["flask", "web"],
        "titles": [
            "Flask-WTF báo lỗi CSRF token missing thì xử lý thế nào?",
            "Cách chia route thành nhiều file bằng Blueprint?",
            "Làm sao truyền dữ liệu từ route sang template Jinja2?",
        ],
    },
    {
        "tags": ["sql", "cơ sở dữ liệu"],
        "titles": [
            "Khi nào nên dùng JOIN, khi nào dùng subquery?",
            "Khóa chính và khóa ngoại khác nhau như thế nào?",
            "Chuẩn hóa dữ liệu đến dạng chuẩn 3NF nghĩa là gì?",
        ],
    },
    {
        "tags": ["git", "github"],
        "titles": [
            "Làm sao giải quyết conflict khi merge branch trong Git?",
            "Khác nhau giữa git fetch và git pull là gì?",
            "Lỡ commit nhầm file chứa mật khẩu thì xóa khỏi lịch sử thế nào?",
        ],
    },
    {
        "tags": ["toán", "giải tích"],
        "titles": [
            "Cách tính giới hạn khi gặp dạng vô định 0/0?",
            "Khi nào dùng đạo hàm riêng thay vì đạo hàm thường?",
        ],
    },
    {
        "tags": ["tiếng anh", "ielts"],
        "titles": [
            "Nên học từ vựng IELTS theo chủ đề hay theo danh sách?",
            "Làm sao cải thiện Writing Task 2 trong vòng 1 tháng?",
        ],
    },
]

QUESTION_INTROS = [
    "Chào mọi người, mình là sinh viên năm {year} và đang gặp một chỗ chưa hiểu.",
    "Mình đang làm bài tập nhóm thì bị vướng ở phần này.",
    "Mình đã tìm trên mạng nhưng vẫn chưa rõ nên lên đây hỏi.",
]
QUESTION_DETAILS = [
    "Mình đã đọc tài liệu trên lớp nhưng vẫn chưa hiểu rõ bản chất.",
    "Mình đã thử vài cách nhưng kết quả vẫn không như mong đợi.",
    "Thầy cô có cho ví dụ trên lớp nhưng mình chưa áp dụng được vào bài của mình.",
]
QUESTION_OUTROS = [
    "Bạn nào có kinh nghiệm chỉ giúp mình với, cảm ơn nhiều!",
    "Mong mọi người giải thích dễ hiểu giúp mình nhé.",
    "Cảm ơn cả nhà đã đọc và hỗ trợ!",
]

ANSWER_BANK = [
    "Bạn thử đọc lại tài liệu chính thức trước, phần ví dụ giải thích khá rõ đó.",
    "Mình từng gặp lỗi này rồi. Bạn kiểm tra lại cấu hình và thứ tự các bước nhé.",
    "Cách đơn giản nhất là chia nhỏ vấn đề ra rồi thử từng phần một.",
    "Bạn có thể gửi thêm đoạn code hoặc đề bài cụ thể không? Mình sẽ xem giúp.",
    "Theo mình thì bạn nên luyện thêm bài tập cơ bản trước khi sang phần nâng cao.",
    "Bạn xem video hướng dẫn trên YouTube, mình thấy nhiều bạn trong lớp cũng học theo cách này.",
    "Đúng rồi, đó là cách làm chuẩn. Bạn chỉ cần chú ý thêm trường hợp đặc biệt là xong.",
    "Mình nghĩ vấn đề nằm ở chỗ bạn hiểu nhầm khái niệm, để mình giải thích lại từ đầu nhé.",
]


# ---------------------------------------------------------------------------
# Hàm hỗ trợ
# ---------------------------------------------------------------------------
def _to_ascii(text):
    """'Nguyễn Đức Anh' -> 'nguyenducanh' (dùng làm username)."""
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", text.lower())


# ---------------------------------------------------------------------------
# Các hàm sinh dữ liệu
# ---------------------------------------------------------------------------
def generate_users(count=10):
    """Sinh danh sách user. Username dài 3-20 ký tự, mật khẩu >= 6 ký tự
    (khớp với ràng buộc của RegistrationForm)."""
    users, used_usernames = [], set()
    while len(users) < count:
        username = _to_ascii(fake.name())[:15] + str(random.randint(1, 99))
        if len(username) < 3 or username in used_usernames:
            continue
        used_usernames.add(username)
        users.append(
            {
                "username": username,
                "email": f"{username}@{random.choice(EMAIL_DOMAINS)}",
                "password": fake.password(length=10),
            }
        )
    return users


def generate_questions(users, count=15):
    """Sinh danh sách câu hỏi ngẫu nhiên, mỗi câu gắn với một tác giả (username)."""
    pool = [
        (title, ", ".join(topic["tags"]))
        for topic in QUESTION_BANK
        for title in topic["titles"]
    ]
    random.shuffle(pool)

    questions = []
    for i in range(count):
        title, tags = pool[i % len(pool)]
        content = " ".join(
            [
                random.choice(QUESTION_INTROS).format(year=random.randint(1, 4)),
                random.choice(QUESTION_DETAILS),
                random.choice(QUESTION_OUTROS),
            ]
        )
        questions.append(
            {
                "title": title,
                "content": content,
                "tags": tags,  # chuỗi cách nhau bằng dấu phẩy, giống QuestionForm
                "author": random.choice(users)["username"],
            }
        )
    return questions


def generate_answers(questions, users, max_per_question=3):
    """Sinh câu trả lời cho các câu hỏi. 'question_index' là vị trí của câu hỏi
    trong list questions. Tác giả câu trả lời cố gắng khác tác giả câu hỏi."""
    answers = []
    for index, question in enumerate(questions):
        others = [u for u in users if u["username"] != question["author"]] or users
        for _ in range(random.randint(0, max_per_question)):
            answers.append(
                {
                    "question_index": index,
                    "content": random.choice(ANSWER_BANK),
                    "author": random.choice(others)["username"],
                }
            )
    return answers


# ===========================================================================
# Khánh: KẾT NỐI VÀ ĐỔ DỮ LIỆU VÀO DATABASE
# ===========================================================================
from app import app
from src.models import db, User, Question, Answer, Tag
from src.extensions import bcrypt

def seed_to_database():
    """Hàm hút dữ liệu từ Faker và đổ vào SQL Server"""
    
    print("⏳ Đang sinh dữ liệu ảo...")
    fake_users = generate_users(10)
    fake_questions = generate_questions(fake_users, 15)
    fake_answers = generate_answers(fake_questions, fake_users, max_per_question=3)

    print("🚀 Đang kết nối Database và bơm dữ liệu...")
    
    # 1. BƠM USERS (Nhớ băm mật khẩu)
    db_users = {} # Tạo dict để lưu User Object, lát nữa móc nối với Câu hỏi
    for u_data in fake_users:
        # Băm pass để tí nữa xài form login thật được
        hashed_pw = bcrypt.generate_password_hash(u_data['password']).decode('utf-8')
        
        user = User(
            username=u_data['username'],
            email=u_data['email'],
            password_hash=hashed_pw,
            role='student'
        )
        db.session.add(user)
        db_users[user.username] = user # Lưu tạm vào biến để lát gán tác giả
        
    db.session.commit() # Lưu User xong mới có ID
    print(f"✅ Đã thêm {len(fake_users)} Users.")

    # 2. BƠM QUESTIONS & TAGS (Xử lý Many-to-Many)
    db_questions = {} # Lưu Question Object để lát gán Câu trả lời
    for i, q_data in enumerate(fake_questions):
        question = Question(
            title=q_data['title'],
            content=q_data['content'],
            author=db_users[q_data['author']] # Lấy object User từ dict trên
        )
        db.session.add(question)
        
        # Xử lý Tags (Cắt chuỗi "python, lập trình" ra)
        tag_names = [t.strip().lower() for t in q_data['tags'].split(',')]
        for tag_name in tag_names:
            if tag_name:
                # Kiểm tra xem tag này đã có trong DB chưa, chưa có thì tạo mới
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                # Gắn tag vào câu hỏi
                question.tags.append(tag)
        
        db_questions[i] = question # Lưu vị trí index để lát gắn câu trả lời
        
    db.session.commit()
    print(f"✅ Đã thêm {len(fake_questions)} Câu hỏi và Tags.")

    # 3. BƠM ANSWERS
    for a_data in fake_answers:
        answer = Answer(
            content=a_data['content'],
            author=db_users[a_data['author']],
            question=db_questions[a_data['question_index']],
            upvotes=random.randint(0, 50) # Cho ngẫu nhiên vài vote nhìn cho xịn
        )
        db.session.add(answer)
        
    db.session.commit()
    print(f"✅ Đã thêm {len(fake_answers)} Câu trả lời.")
    print("🎉 HOÀN TẤT SEED DATA! Mở SQL Server lên xem thành quả nhé!")

# ---------------------------------------------------------------------------
# CHẠY FILE: python seed_data.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # CỰC KỲ QUAN TRỌNG: Phải bọc trong app_context() thì mới can thiệp DB được
    with app.app_context():
        # Xóa sạch data cũ để tránh lỗi trùng lặp (Duplicate Key) khi chạy nhiều lần
        print("🧹 Đang dọn dẹp Database cũ...")
        db.session.query(Answer).delete()
        db.session.query(Question.tags.property.secondary).delete() # Xóa bảng phụ N-N
        db.session.query(Question).delete()
        db.session.query(Tag).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        # Chạy hàm bơm data
        seed_to_database()