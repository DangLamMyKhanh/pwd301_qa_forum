import bleach
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, current_app
from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload
from flask_login import login_required, current_user
from src.models import db, Question, Answer, Tag, SecurityAuditLog, Vote, adjust_reputation, Permission
from src.forms import QuestionForm, AnswerForm
from src.auth import role_required, permission_required

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

    # Tối ưu hóa N+1 Query: Sử dụng Eager Loading (joinedload, selectinload) theo chuẩn Rubric CLO4
    # Thay vì lazy load 1 + 20 (author) + 20 (tags) + 20 (answers) = 61 queries,
    # Eager loading tải trước dữ liệu liên kết, giảm xuống còn đúng 3 queries.
    query = Question.query.options(
        joinedload(Question.author),
        selectinload(Question.tags),
        selectinload(Question.answers)
    )

    # Ẩn câu hỏi vi phạm đối với sinh viên thông thường (Moderator và Admin vẫn thấy để kiểm duyệt)
    if not (current_user.is_authenticated and current_user.role in ['admin', 'moderator']):
        if current_user.is_authenticated:
            query = query.filter((Question.is_hidden == False) | (Question.user_id == current_user.id))
        else:
            query = query.filter(Question.is_hidden == False)

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
        query = query.order_by((Question.upvotes + subquery).desc(), Question.created_at.desc(), Question.id.desc())
    else:
        sort_by = 'newest'
        query = query.order_by(Question.created_at.desc(), Question.id.desc())

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
    # Tối ưu hóa N+1: Eager load thông tin Author, Tags, Answers và Author của từng Answer
    question = Question.query.options(
        joinedload(Question.author),
        selectinload(Question.tags),
        selectinload(Question.answers).joinedload(Answer.author)
    ).get_or_404(question_id)

    # Tăng lượt xem cho câu hỏi (Chỉ tăng nếu người xem không phải là tác giả của câu hỏi)
    if not (current_user.is_authenticated and current_user.id == question.user_id):
        question.views = (question.views or 0) + 1
        db.session.commit()

    form = AnswerForm()

    # Truy vấn trạng thái bình chọn của user hiện tại cho câu hỏi và các câu trả lời
    user_votes = {}
    user_question_vote = 0
    if current_user.is_authenticated:
        q_vote = Vote.query.filter_by(user_id=current_user.id, question_id=question.id).first()
        if q_vote:
            user_question_vote = q_vote.vote_type

        if question.answers:
            answer_ids = [a.id for a in question.answers]
            votes = Vote.query.filter_by(user_id=current_user.id).filter(Vote.answer_id.in_(answer_ids)).all()
            user_votes = {v.answer_id: v.vote_type for v in votes}

    return render_template(
        'question_detail.html',
        question=question,
        form=form,
        user_votes=user_votes,
        user_question_vote=user_question_vote
    )


# ===========================================================================
# 3. GỬI CÂU TRẢ LỜI CHO CÂU HỎI
# ===========================================================================
@main_bp.route('/question/<int:question_id>/answer', methods=['POST'])
@login_required
def add_answer(question_id):
    question = Question.query.get_or_404(question_id)

    # Nếu câu hỏi đã bị Admin khóa -> Chặn không cho gửi câu trả lời
    if question.is_locked and current_user.role != 'admin':
        flash("Câu hỏi này đã bị khóa bởi Quản trị viên, không thể gửi câu trả lời mới!", "warning")
        return redirect(url_for('main.question_detail', question_id=question.id))

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

        # 4.2. KIỂM TRA TRÙNG LẶP TIÊU ĐỀ CÂU HỎI
        title_text = form.title.data.strip()
        duplicate_q = Question.query.filter_by(user_id=current_user.id, title=title_text).first()
        if duplicate_q:
            flash("Bạn đã đăng một câu hỏi có tiêu đề tương tự rồi!", "warning")
            return redirect(url_for('main.ask_question'))

        # 4.3. BẢO MẬT: CHỐNG XSS BẰNG BLEACH
        raw_content = form.content.data.strip()
        allowed_tags = ['b', 'i', 'strong', 'em', 'p', 'a', 'code', 'pre', 'ul', 'ol', 'li']
        clean_content = bleach.clean(raw_content, tags=allowed_tags, strip=True)

        new_q = Question(
            title=title_text,
            content=clean_content,
            user_id=current_user.id
        )

        # 4.4. XỬ LÝ TAGS
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
# 5. XÓA CÂU HỎI (PHÂN QUYỀN RBAC: CHỈ ADMIN HOẶC TÁC GIẢ BÀI VIẾT)
# (Theo Rubric: Admin delete/lock posts; Moderator hide violations; Student ask/answer)
# ===========================================================================
@main_bp.route('/question/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)

    # Chỉ Admin hoặc chính tác giả câu hỏi mới có quyền xóa
    is_admin = current_user.role == 'admin'
    is_owner = current_user.id == question.user_id

    if not (is_admin or is_owner):
        # Ghi nhận nỗ lực xóa trái phép vào Audit Log
        log = SecurityAuditLog(
            user_id=current_user.id,
            ip_address=request.remote_addr,
            action=f"Cảnh báo RBAC/IDOR: User '{current_user.username}' (role: {current_user.role}) cố tình xóa câu hỏi #{question.id} mà không có quyền"
        )
        db.session.add(log)
        db.session.commit()
        abort(403)

    db.session.delete(question)
    db.session.commit()

    flash("Đã xóa câu hỏi thành công!", "success")
    return redirect(url_for('main.index'))


# ===========================================================================
# 6. XÓA CÂU TRẢ LỜI (PHÂN QUYỀN RBAC: CHỈ ADMIN HOẶC TÁC GIẢ BÀI VIẾT)
# ===========================================================================
@main_bp.route('/answer/<int:answer_id>/delete', methods=['POST'])
@login_required
def delete_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    question_id = answer.question_id

    is_admin = current_user.role == 'admin'
    is_owner = current_user.id == answer.user_id

    if not (is_admin or is_owner):
        log = SecurityAuditLog(
            user_id=current_user.id,
            ip_address=request.remote_addr,
            action=f"Cảnh báo RBAC/IDOR: User '{current_user.username}' (role: {current_user.role}) cố tình xóa câu trả lời #{answer.id} mà không có quyền"
        )
        db.session.add(log)
        db.session.commit()
        abort(403)

    db.session.delete(answer)
    db.session.commit()

    flash("Đã xóa câu trả lời thành công!", "success")
    return redirect(url_for('main.question_detail', question_id=question_id))


# ===========================================================================
# 7. KHÓA / MỞ KHÓA BÀI VIẾT (PHÂN QUYỀN RBAC: ADMIN ONLY - SỬ DỤNG @permission_required)
# ===========================================================================
@main_bp.route('/question/<int:question_id>/lock', methods=['POST'])
@login_required
@permission_required(Permission.LOCK_POST)
def lock_question(question_id):
    question = Question.query.get_or_404(question_id)
    question.is_locked = not question.is_locked

    log = SecurityAuditLog(
        user_id=current_user.id,
        ip_address=request.remote_addr,
        action=f"Admin '{current_user.username}' đã {'khóa' if question.is_locked else 'mở khóa'} câu hỏi #{question.id}"
    )
    db.session.add(log)
    db.session.commit()

    flash("Đã khóa câu hỏi!" if question.is_locked else "Đã mở khóa câu hỏi!", "success")
    return redirect(url_for('main.question_detail', question_id=question.id))


# ===========================================================================
# 8. ẨN / HIỆN BÀI VIẾT VI PHẠM (PHÂN QUYỀN RBAC: MODERATOR & ADMIN - SỬ DỤNG @permission_required)
# ===========================================================================
@main_bp.route('/question/<int:question_id>/hide', methods=['POST'])
@login_required
@permission_required(Permission.HIDE_VIOLATIONS)
def hide_question(question_id):
    question = Question.query.get_or_404(question_id)
    question.is_hidden = not question.is_hidden

    log = SecurityAuditLog(
        user_id=current_user.id,
        ip_address=request.remote_addr,
        action=f"Kiểm duyệt viên '{current_user.username}' đã {'ẩn' if question.is_hidden else 'bỏ ẩn'} câu hỏi #{question.id}"
    )
    db.session.add(log)
    db.session.commit()

    flash("Đã ẩn câu hỏi vi phạm!" if question.is_hidden else "Đã khôi phục hiển thị câu hỏi!", "info")
    return redirect(url_for('main.question_detail', question_id=question.id))


@main_bp.route('/answer/<int:answer_id>/hide', methods=['POST'])
@login_required
@permission_required(Permission.HIDE_VIOLATIONS)
def hide_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    answer.is_hidden = not answer.is_hidden

    log = SecurityAuditLog(
        user_id=current_user.id,
        ip_address=request.remote_addr,
        action=f"Kiểm duyệt viên '{current_user.username}' đã {'ẩn' if answer.is_hidden else 'bỏ ẩn'} câu trả lời #{answer.id}"
    )
    db.session.add(log)
    db.session.commit()

    flash("Đã ẩn câu trả lời vi phạm!" if answer.is_hidden else "Đã khôi phục câu trả lời!", "info")
    return redirect(url_for('main.question_detail', question_id=answer.question_id))


# ===========================================================================
# 9. ĐÁNH DẤU "BEST ANSWER" (TÁC GIẢ CÂU HỎI ONLY)
# ===========================================================================
@main_bp.route('/answer/<int:answer_id>/best', methods=['POST'])
@login_required
def toggle_best_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    question = answer.question

    # Chỉ tác giả câu hỏi mới có quyền chọn Best Answer
    if question.user_id != current_user.id:
        abort(403)

    if answer.is_best:
        answer.is_best = False
        adjust_reputation(answer.author, -15)
        flash("Đã bỏ chọn câu trả lời hay nhất!", "info")
    else:
        # Bỏ chọn best answer cũ nếu có
        for other in question.answers:
            if other.is_best and other.id != answer.id:
                other.is_best = False
                adjust_reputation(other.author, -15)

        answer.is_best = True
        adjust_reputation(answer.author, 15)
        flash("Đã đánh dấu là câu trả lời hay nhất (+15 điểm uy tín cho tác giả)!", "success")

    db.session.commit()
    return redirect(url_for('main.question_detail', question_id=question.id))
