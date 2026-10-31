from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

# Khởi tạo công cụ Database (Chưa kết nối)
db = SQLAlchemy()

# 1. BẢNG TRUNG GIAN (Cho quan hệ Nhiều-Nhiều giữa Câu hỏi và Tag)
question_tag_m2m = db.Table('question_tag',
    db.Column('question_id', db.Integer, db.ForeignKey('questions.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

# 2. BẢNG NGƯỜI DÙNG
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False) # Bảo mật: Chỉ lưu Hash
    role = db.Column(db.String(20), default='student') # Phân quyền: student, mod, admin
    
    # Quan hệ 1-N: 1 User có nhiều Câu hỏi, nhiều Câu trả lời, nhiều Vote
    questions = db.relationship('Question', backref='author', lazy=True)
    answers = db.relationship('Answer', backref='author', lazy=True)
    votes = db.relationship('Vote', backref='user', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# 3. BẢNG CÂU HỎI
class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(200), nullable=False)
    content = db.Column(db.UnicodeText, nullable=False)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Quan hệ 1-N với Answer, N-N với Tag
    answers = db.relationship('Answer', backref='question', lazy=True, cascade="all, delete-orphan")
    tags = db.relationship('Tag', secondary=question_tag_m2m, backref=db.backref('questions', lazy='dynamic'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# 4. BẢNG CÂU TRẢ LỜI
class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.UnicodeText, nullable=False)
    upvotes = db.Column(db.Integer, default=0) # Tổng điểm vote
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)

    # Quan hệ 1-N với bảng Vote
    votes = db.relationship('Vote', backref='answer', lazy=True, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# 5. BẢNG CHỦ ĐỀ (TAGS)
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50), unique=True, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# 6. BẢNG LOG BẢO MẬT (Audit Log)
class SecurityAuditLog(db.Model):
    __tablename__ = 'security_audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True) # Có thể null nếu chưa đăng nhập
    ip_address = db.Column(db.String(50), nullable=False)
    action = db.Column(db.Unicode(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# 7. BẢNG VOTE (Theo Rubric Step 2: Mỗi user chỉ vote 1 lần / câu trả lời)
class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=True)
    vote_type = db.Column(db.Integer, nullable=False, default=1) # +1: Upvote, -1: Downvote
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'answer_id', name='uq_user_answer_vote'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
