"""
forms.py - Các biểu mẫu (Flask-WTF) cho Student Q&A Forum.

Gồm 4 form:
    - RegistrationForm : đăng ký tài khoản
    - LoginForm        : đăng nhập
    - QuestionForm     : đặt câu hỏi
    - AnswerForm       : trả lời câu hỏi
"""

# ---------------------------------------------------------------------------
# Task 1.1: Cấu hình thư viện
# ---------------------------------------------------------------------------
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp


# ---------------------------------------------------------------------------
# Task 1.2: Form đăng ký
# ---------------------------------------------------------------------------
class RegistrationForm(FlaskForm):
    username = StringField(
        "Tên đăng nhập",
        validators=[
            DataRequired(message="Vui lòng nhập tên đăng nhập."),
            Length(min=3, max=20, message="Tên đăng nhập phải từ 3 đến 20 ký tự."),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message="Tên đăng nhập chỉ được chứa chữ cái, số và dấu gạch dưới.",
            ),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Vui lòng nhập email."),
            Email(message="Email không đúng định dạng."),
            Length(max=100, message="Email không được vượt quá 100 ký tự."),
        ],
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[
            DataRequired(message="Vui lòng nhập mật khẩu."),
            Length(min=6, message="Mật khẩu phải có ít nhất 6 ký tự."),
        ],
    )
    confirm_password = PasswordField(
        "Xác nhận mật khẩu",
        validators=[
            DataRequired(message="Vui lòng nhập lại mật khẩu."),
            EqualTo("password", message="Mật khẩu xác nhận không khớp."),
        ],
    )
    submit = SubmitField("Đăng ký")


# ---------------------------------------------------------------------------
# Task 1.3: Form đăng nhập
# ---------------------------------------------------------------------------
class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Vui lòng nhập email."),
            Email(message="Email không đúng định dạng."),
            Length(max=100, message="Email không được vượt quá 100 ký tự."),
        ],
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[DataRequired(message="Vui lòng nhập mật khẩu.")],
    )
    submit = SubmitField("Đăng nhập")


# ---------------------------------------------------------------------------
# Task 1.4: Form câu hỏi & câu trả lời
# ---------------------------------------------------------------------------
class QuestionForm(FlaskForm):
    title = StringField(
        "Tiêu đề",
        validators=[
            DataRequired(message="Vui lòng nhập tiêu đề câu hỏi."),
            Length(max=200, message="Tiêu đề không được vượt quá 200 ký tự."),
        ],
    )
    content = TextAreaField(
        "Nội dung",
        validators=[DataRequired(message="Vui lòng nhập nội dung câu hỏi.")],
    )
    tags = StringField(
        "Nhãn",
        validators=[DataRequired(message="Vui lòng nhập ít nhất một nhãn.")],
        description="Nhập các nhãn cách nhau bằng dấu phẩy, ví dụ: python, flask, sql",
        render_kw={"placeholder": "python, flask, sql"},
    )
    submit = SubmitField("Đăng câu hỏi")


class AnswerForm(FlaskForm):
    content = TextAreaField(
        "Câu trả lời của bạn",
        validators=[DataRequired(message="Vui lòng nhập nội dung câu trả lời.")],
    )
    submit = SubmitField("Gửi câu trả lời")