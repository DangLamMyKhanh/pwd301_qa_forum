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


# ---------------------------------------------------------------------------
# Chạy thử: python seed_data.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Tránh lỗi hiển thị tiếng Việt trên terminal Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    users = generate_users(10)
    questions = generate_questions(users, 8)
    answers = generate_answers(questions, users)

    print("=" * 60)
    print(f"DANH SÁCH {len(users)} USER")
    print("=" * 60)
    for u in users:
        print(f"- {u['username']:<20} | {u['email']:<35} | mật khẩu: {u['password']}")

    print()
    print("=" * 60)
    print(f"DANH SÁCH {len(questions)} CÂU HỎI (kèm câu trả lời)")
    print("=" * 60)
    for i, q in enumerate(questions):
        print(f"\n[Q{i + 1}] {q['title']}")
        print(f"     Nhãn: {q['tags']} | Người hỏi: {q['author']}")
        print(f"     {q['content']}")
        for a in (a for a in answers if a["question_index"] == i):
            print(f"       -> {a['author']}: {a['content']}")