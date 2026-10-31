import bleach
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, current_app
from sqlalchemy import func
from flask_login import login_required, current_user
from src.models import db, Question, Answer, Tag, SecurityAuditLog, Vote
from src.forms import QuestionForm, AnswerForm

main_bp = Blueprint('main', __name__)


# ===========================================================================
# 1. TRANG CHỦ & DANH SÁCH CÂU HỎI (PHÂN TRANG 20 CÂU/TRANG + SEARCH + LỌC TAG)
# ===========================================================================
@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    tag_filter = request.args.get('tag', '').strip()
    sort_by = request.args.get('sort', 'newest').strip()

    query = Question.query

    # Tìm kiếm theo từ khóa (tiêu đề hoặc nội dung)
    if search_query:
        query = query.filter(
            Question.title.ilike(f'%{search_query}%') |
            Question.content.ilike(f'%{search_query}%')
        )

    # Lọc theo Tag
    if tag_filter:
        query = query.filter(Question.tags.any(Tag.name == tag_filter))

    # Sắp xếp theo Newest (Mới nhất) hoặc Votes (Nhiều vote nhất theo Rubric Topic 5)
    if sort_by == 'votes':
        subquery = (
            db.session.query(func.coalesce(func.sum(Answer.upvotes), 0))
            .filter(Answer.question_id == Question.id)
            .correlate(Question)
            .scalar_subquery()
        )
        query = query.order_by(subquery.desc(), Question.created_at.desc())
    else:
        sort_by = 'newest'
        query = query.order_by(Question.created_at.desc())

    # Phân trang: lấy số lượng từ cấu hình POSTS_PER_PAGE trong config.py
    per_page = current_app.config.get('POSTS_PER_PAGE', 20)
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    questions = pagination.items
    all_tags = Tag.query.all()

    return render_template(
        'index.html',
        questions=questions,
        pagination=pagination,
        all_tags=all_tags,
        search_query=search_query,
        selected_tag=tag_filter,
        sort_by=sort_by,
        jwt_token=session.get('jwt_token')
    )


# ===========================================================================
# 2. CHI TIẾT CÂU HỎI & CÂU TRẢ LỜI
# ===========================================================================
@main_bp.route('/question/<int:question_id>')
def question_detail(question_id):
    question = Question.query.get_or_404(question_id)

    # Tăng lượt xem cho câu hỏi
    question.views = (question.views or 0) + 1
    db.session.commit()

    form = AnswerForm()

    # Truy vấn trạng thái bình chọn của user hiện tại cho các câu trả lời
    user_votes = {}
    if current_user.is_authenticated and question.answers:
        answer_ids = [a.id for a in question.answers]
        votes = Vote.query.filter_by(user_id=current_user.id).filter(Vote.answer_id.in_(answer_ids)).all()
        user_votes = {v.answer_id: v.vote_type for v in votes}

    return render_template('question_detail.html', question=question, form=form, user_votes=user_votes)


# ===========================================================================
# 3. GỬI CÂU TRẢ LỜI CHO CÂU HỎI
# ===========================================================================
@main_bp.route('/question/<int:question_id>/answer', methods=['POST'])
@login_required
def add_answer(question_id):
    question = Question.query.get_or_404(question_id)
    form = AnswerForm()

    if form.validate_on_submit():
        raw_content = form.content.data.strip()

        # Chống XSS bằng Bleach
        allowed_tags = ['b', 'i', 'strong', 'em', 'p', 'a', 'code', 'pre', 'ul', 'ol', 'li']
        clean_content = bleach.clean(raw_content, tags=allowed_tags, strip=True)

        answer = Answer(
            content=clean_content,
            user_id=current_user.id,
            question_id=question.id,
            upvotes=0
        )
        db.session.add(answer)
        db.session.commit()

        flash("Câu trả lời của bạn đã được đăng thành công!", "success")
        return redirect(url_for('main.question_detail', question_id=question.id))

    # Nếu form không hợp lệ (ví dụ: để trống)
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{error}", "danger")

    return redirect(url_for('main.question_detail', question_id=question.id))


# ===========================================================================
# 4. ĐẶT CÂU HỎI MỚI (CHỐNG SPAM + CHỐNG XSS + FLASK-WTF)
# ===========================================================================
@main_bp.route('/ask', methods=['GET', 'POST'])
@login_required
def ask_question():
    form = QuestionForm()

    if form.validate_on_submit():
        # 4.1. BẢO MẬT: ANTI-SPAM & RATE LIMITING
        last_question = Question.query.filter_by(user_id=current_user.id).order_by(Question.created_at.desc()).first()

        if last_question:
            time_diff = datetime.utcnow() - last_question.created_at
            if time_diff < timedelta(minutes=1):
                # Ghi log bảo mật vào DB
                log = SecurityAuditLog(
                    user_id=current_user.id,
                    ip_address=request.remote_addr,
                    action="Spam Alert: Cố tình đăng câu hỏi liên tục dưới 1 phút"
                )
                db.session.add(log)
                db.session.commit()

                flash("Bạn thao tác quá nhanh! Vui lòng đợi 1 phút trước khi đăng bài tiếp.", "danger")
                return redirect(url_for('main.ask_question'))

        # 4.2. BẢO MẬT: CHỐNG XSS BẰNG BLEACH
        raw_content = form.content.data.strip()
        allowed_tags = ['b', 'i', 'strong', 'em', 'p', 'a', 'code', 'pre', 'ul', 'ol', 'li']
        clean_content = bleach.clean(raw_content, tags=allowed_tags, strip=True)

        new_q = Question(
            title=form.title.data.strip(),
            content=clean_content,
            user_id=current_user.id
        )

        # 4.3. XỬ LÝ TAGS
        raw_tags = form.tags.data or ''
        tag_names = [t.strip() for t in raw_tags.split(',') if t.strip()]
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
                db.session.add(tag)
            new_q.tags.append(tag)

        db.session.add(new_q)
        db.session.commit()

        flash("Đăng câu hỏi thành công!", "success")
        return redirect(url_for('main.question_detail', question_id=new_q.id))

    return render_template('ask_question.html', form=form)


# ===========================================================================
# 5. XÓA CÂU HỎI (PHÂN QUYỀN RBAC: ADMIN / MODERATOR HOẶC TÁC GIẢ BÀI VIẾT)
# ===========================================================================
@main_bp.route('/question/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)

    # Kiểm tra phân quyền RBAC & Quyền sở hữu (Ownership Check chống IDOR)
    is_admin_or_mod = current_user.role in ['admin', 'moderator', 'mod']
    is_owner = current_user.id == question.user_id

    if not (is_admin_or_mod or is_owner):
        # Ghi nhận nỗ lực xóa trái phép vào Audit Log
        log = SecurityAuditLog(
            user_id=current_user.id,
            ip_address=request.remote_addr,
            action=f"Cảnh báo IDOR: User '{current_user.username}' cố tình xóa câu hỏi #{question.id} mà không có quyền"
        )
        db.session.add(log)
        db.session.commit()
        abort(403)

    db.session.delete(question)
    db.session.commit()

    flash("Đã xóa câu hỏi thành công!", "success")
    return redirect(url_for('main.index'))


# ===========================================================================
# 6. XÓA CÂU TRẢ LỜI (PHÂN QUYỀN RBAC: ADMIN / MODERATOR HOẶC TÁC GIẢ BÀI VIẾT)
# ===========================================================================
@main_bp.route('/answer/<int:answer_id>/delete', methods=['POST'])
@login_required
def delete_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    question_id = answer.question_id

    is_admin_or_mod = current_user.role in ['admin', 'moderator', 'mod']
    is_owner = current_user.id == answer.user_id

    if not (is_admin_or_mod or is_owner):
        log = SecurityAuditLog(
            user_id=current_user.id,
            ip_address=request.remote_addr,
            action=f"Cảnh báo IDOR: User '{current_user.username}' cố tình xóa câu trả lời #{answer.id} mà không có quyền"
        )
        db.session.add(log)
        db.session.commit()
        abort(403)

    db.session.delete(answer)
    db.session.commit()

    flash("Đã xóa câu trả lời thành công!", "success")
    return redirect(url_for('main.question_detail', question_id=question_id))
