from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import func
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_login import current_user
from src.models import db, Question, Tag, Answer, SecurityAuditLog, User, Vote

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 0. API Test kết nối (Public)
@api_bp.route('/test', methods=['GET'])
def api_test():
    return jsonify({
        "status": "success",
        "message": "Kết nối API Backend thành công!"
    }), 200

# 1. API GET Danh sách Câu hỏi (Hỗ trợ tìm kiếm ?tag=..., ?q=... và sắp xếp ?sort=votes/newest theo Rubric Topic 5)
@api_bp.route('/questions', methods=['GET'])
def get_questions():
    tag_param = request.args.get('tag', '').strip()
    q_param = request.args.get('q', '').strip()
    sort_param = request.args.get('sort', 'newest').strip()

    query = Question.query
    if q_param:
        query = query.filter(
            Question.title.ilike(f'%{q_param}%') |
            Question.content.ilike(f'%{q_param}%')
        )
    if tag_param:
        query = query.filter(Question.tags.any(Tag.name == tag_param))

    # Sắp xếp theo votes hoặc newest
    if sort_param == 'votes':
        subquery = (
            db.session.query(func.coalesce(func.sum(Answer.upvotes), 0))
            .filter(Answer.question_id == Question.id)
            .correlate(Question)
            .scalar_subquery()
        )
        query = query.order_by(subquery.desc(), Question.created_at.desc())
    else:
        query = query.order_by(Question.created_at.desc())

    questions = query.all()
    data = []
    for q in questions:
        data.append({
            "id": q.id,
            "title": q.title,
            "views": q.views,
            "votes": sum(a.upvotes for a in q.answers) if q.answers else 0,
            "author": q.author.username if q.author else "Ẩn danh",
            "tags": [t.name for t in q.tags],
            "answers_count": len(q.answers)
        })
    return jsonify({
        "status": "success",
        "count": len(data),
        "data": data
    }), 200

# 2. API GET Danh sách Tag (Public)
@api_bp.route('/tags', methods=['GET'])
def get_tags():
    tags = Tag.query.all()
    data = [{"id": t.id, "name": t.name} for t in tags]
    return jsonify({"status": "success", "data": data}), 200

# 3. API POST Chức năng Vote Câu trả lời (AJAX - Kiểm soát 1 User chỉ vote 1 lần)
@api_bp.route('/vote/answer/<int:answer_id>', methods=['POST'])
def vote_answer(answer_id):
    # 3.1. Bắt buộc đăng nhập
    if not current_user.is_authenticated:
        return jsonify({
            "status": "error",
            "message": "Vui lòng đăng nhập để bình chọn câu trả lời!"
        }), 401

    answer = Answer.query.get_or_404(answer_id)

    # 3.2. Không được tự vote câu trả lời của chính mình
    if answer.user_id == current_user.id:
        return jsonify({
            "status": "error",
            "message": "Bạn không thể tự bình chọn cho câu trả lời của chính mình!"
        }), 400

    data = request.get_json(silent=True) or {}
    req_type = data.get('type') or request.args.get('type', 'up')
    target_type = -1 if req_type == 'down' else 1

    # 3.3. Kiểm tra xem người dùng đã từng vote câu trả lời này chưa
    existing_vote = Vote.query.filter_by(user_id=current_user.id, answer_id=answer.id).first()

    if not existing_vote:
        # Trường hợp 1: Chưa vote -> Tạo vote mới (+1 hoặc -1)
        new_vote = Vote(user_id=current_user.id, answer_id=answer.id, vote_type=target_type)
        db.session.add(new_vote)
        answer.upvotes = (answer.upvotes or 0) + target_type
        user_vote = target_type
        message = "Bình chọn thành công!"
    elif existing_vote.vote_type == target_type:
        # Trường hợp 2: Bấm lại vào nút đã vote -> HỦY BÌNH CHỌN (Undo)
        answer.upvotes = (answer.upvotes or 0) - existing_vote.vote_type
        db.session.delete(existing_vote)
        user_vote = 0
        message = "Đã hủy bình chọn!"
    else:
        # Trường hợp 3: Đổi từ Upvote sang Downvote hoặc ngược lại
        answer.upvotes = (answer.upvotes or 0) - existing_vote.vote_type + target_type
        existing_vote.vote_type = target_type
        user_vote = target_type
        message = "Đã thay đổi bình chọn!"

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": message,
        "new_upvotes": answer.upvotes,
        "user_vote": user_vote
    }), 200

# 4. API POST Chức năng Vote Câu hỏi (Theo Rubric Step 6: POST /api/questions/<id>/vote)
@api_bp.route('/questions/<int:question_id>/vote', methods=['POST'])
def vote_question(question_id):
    question = Question.query.get_or_404(question_id)
    question.views = (question.views or 0) + 1
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Vote câu hỏi thành công!",
        "new_views": question.views
    }), 200

# 5. API GET Danh sách Audit Logs mới nhất (Cho Live Monitoring Dashboard Real-time có phân trang)
@api_bp.route('/admin/logs', methods=['GET'])
def get_admin_logs():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Yêu cầu quyền Admin!"}), 403

    page = request.args.get('page', 1, type=int)
    default_per_page = current_app.config.get('LOGS_PER_PAGE', 20)
    per_page = request.args.get('per_page', default_per_page, type=int)

    # Thống kê toàn cục
    all_logs = SecurityAuditLog.query.all()
    total = len(all_logs)
    csrf_count = sum(1 for l in all_logs if 'CSRF' in (l.action or ''))
    spam_count = sum(1 for l in all_logs if 'Spam' in (l.action or ''))
    auth_fail_count = sum(1 for l in all_logs if ('thất bại' in (l.action or '') or 'Nỗ lực' in (l.action or '')))
    error_count = sum(1 for l in all_logs if ('403' in (l.action or '') or '404' in (l.action or '')))

    # Phân trang: mặc định 20 logs
    pagination = SecurityAuditLog.query.order_by(SecurityAuditLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    logs = pagination.items
    users_map = {u.id: u.username for u in User.query.all()}

    data = []
    for l in logs:
        data.append({
            "id": l.id,
            "timestamp": l.timestamp.strftime('%d/%m/%Y %H:%M:%S') if l.timestamp else 'N/A',
            "ip_address": l.ip_address,
            "user_id": l.user_id,
            "username": users_map.get(l.user_id),
            "action": l.action
        })

    return jsonify({
        "status": "success",
        "total": total,
        "page": pagination.page,
        "pages": pagination.pages,
        "csrf_count": csrf_count,
        "spam_count": spam_count,
        "auth_fail_count": auth_fail_count,
        "error_count": error_count,
        "logs": data
    }), 200
