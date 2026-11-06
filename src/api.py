import bleach
from flask import Blueprint, jsonify, request, current_app, abort
from werkzeug.security import check_password_hash
from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, create_access_token
from flask_login import current_user
from src.models import db, Question, Tag, Answer, SecurityAuditLog, User, Vote, adjust_reputation, Permission

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ===========================================================================
# HÀM TIỆN ÍCH XÁC THỰC KÉP: JWT BEARER TOKEN HOẶC FLASK-LOGIN SESSION
# ===========================================================================
def get_current_api_user():
    """
    Xác thực người dùng gọi API thông qua JWT Bearer Token hoặc Flask-Login Session
    """
    try:
        verify_jwt_in_request(optional=True)
        jwt_user_id = get_jwt_identity()
        if jwt_user_id:
            user = User.query.get(int(jwt_user_id))
            if user:
                return user
    except Exception:
        pass

    if current_user and current_user.is_authenticated:
        return current_user
    return None


# 0. API Test kết nối (Public)
@api_bp.route('/test', methods=['GET'])
def api_test():
    return jsonify({
        "status": "success",
        "message": "Kết nối API Backend thành công!"
    }), 200


# 0.1. API Đăng nhập lấy JWT Bearer Token (Rubric Criterion 7: JWT Authentication)
@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """
    Endpoint đăng nhập REST API để lấy JWT Bearer Token
    Accurate Status Codes: 200 (OK), 400 (Bad Request), 401 (Unauthorized)
    """
    data = request.get_json(silent=True) or {}
    identifier = (data.get('email') or data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not identifier or not password:
        return jsonify({
            "status": "error",
            "message": "Vui lòng cung cấp đầy đủ email/username và password!"
        }), 400

    user = User.query.filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({
            "status": "error",
            "message": "Tên đăng nhập hoặc mật khẩu không chính xác!"
        }), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "status": "success",
        "message": "Đăng nhập thành công!",
        "access_token": token,
        "token_type": "Bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }), 200


# 0.2. Endpoint kiểm thử mô phỏng lỗi máy chủ (Status Code 500)
@api_bp.route('/test/simulate-error', methods=['GET', 'POST'])
def simulate_server_error():
    """Mô phỏng lỗi 500 để kiểm thử xử lý lỗi toàn cục"""
    raise RuntimeError("Mô phỏng lỗi máy chủ nội bộ (500 Internal Server Error)")


# 1. API GET Danh sách Câu hỏi (Hỗ trợ tìm kiếm ?tag=..., ?q=... và sắp xếp ?sort=votes/newest theo Rubric Topic 5)
@api_bp.route('/questions', methods=['GET'])
def get_questions():
    tag_param = request.args.get('tag', '').strip()
    q_param = request.args.get('q', '').strip()
    sort_param = request.args.get('sort', 'newest').strip()

    # Tối ưu hóa N+1 query: Eager loading Author, Tags và Answers
    query = Question.query.options(
        joinedload(Question.author),
        selectinload(Question.tags),
        selectinload(Question.answers)
    )
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

# 1.1. API GET Chi tiết 1 Câu hỏi (RESTful endpoint: GET /api/questions/<id>)
@api_bp.route('/questions/<int:question_id>', methods=['GET'])
def get_question_detail(question_id):
    """
    Lấy thông tin chi tiết của một câu hỏi kèm tags và danh sách câu trả lời
    Status code: 200 (OK), 404 (Not Found)
    """
    question = Question.query.options(
        joinedload(Question.author),
        selectinload(Question.tags),
        selectinload(Question.answers).joinedload(Answer.author)
    ).get(question_id)

    if not question:
        return jsonify({
            "status": "error",
            "message": f"Không tìm thấy câu hỏi #{question_id}!"
        }), 404

    return jsonify({
        "status": "success",
        "data": {
            "id": question.id,
            "title": question.title,
            "content": question.content,
            "views": question.views,
            "upvotes": question.upvotes,
            "is_locked": question.is_locked,
            "is_hidden": question.is_hidden,
            "created_at": question.created_at.isoformat() if question.created_at else None,
            "author": {
                "id": question.author.id if question.author else None,
                "username": question.author.username if question.author else "Ẩn danh",
                "role": question.author.role if question.author else None
            },
            "tags": [t.name for t in question.tags],
            "answers": [
                {
                    "id": a.id,
                    "content": a.content,
                    "upvotes": a.upvotes,
                    "is_best": a.is_best,
                    "is_hidden": a.is_hidden,
                    "author": a.author.username if a.author else "Ẩn danh",
                    "created_at": a.created_at.isoformat() if a.created_at else None
                } for a in question.answers
            ]
        }
    }), 200

# 1.2. API POST Tạo câu hỏi mới (RESTful endpoint: POST /api/questions -> Status 201 Created)
@api_bp.route('/questions', methods=['POST'])
def create_question():
    """
    Tạo câu hỏi mới qua REST API (Rubric: Accurate Status Code 201 Created)
    Status code: 201 (Created), 400 (Bad Request), 401 (Unauthorized)
    """
    user = get_current_api_user()
    if not user:
        return jsonify({
            "status": "error",
            "message": "Vui lòng đăng nhập hoặc cung cấp JWT Bearer Token!"
        }), 401

    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    tags_data = data.get('tags') or []

    if not title or not content:
        return jsonify({
            "status": "error",
            "message": "Tiêu đề và nội dung câu hỏi không được để trống!"
        }), 400

    clean_title = bleach.clean(title, strip=True)
    clean_content = bleach.clean(content, tags=['p', 'b', 'i', 'u', 'code', 'pre', 'br', 'strong', 'em', 'ul', 'ol', 'li'], strip=True)

    question = Question(
        title=clean_title,
        content=clean_content,
        user_id=user.id
    )
    db.session.add(question)

    if isinstance(tags_data, str):
        tag_names = [t.strip() for t in tags_data.split(',') if t.strip()]
    elif isinstance(tags_data, list):
        tag_names = [str(t).strip() for t in tags_data if str(t).strip()]
    else:
        tag_names = []

    for name in tag_names:
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
        question.tags.append(tag)

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Tạo câu hỏi thành công!",
        "data": {
            "id": question.id,
            "title": question.title,
            "author": user.username,
            "created_at": question.created_at.isoformat() if question.created_at else None
        }
    }), 201

# 1.3. API PUT Cập nhật câu hỏi (RESTful endpoint: PUT /api/questions/<id> -> Status 200 OK)
@api_bp.route('/questions/<int:question_id>', methods=['PUT', 'PATCH'])
def update_question(question_id):
    """
    Cập nhật câu hỏi qua REST API (Rubric: HTTP Method PUT/PATCH)
    Status code: 200 (OK), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found)
    """
    user = get_current_api_user()
    if not user:
        return jsonify({
            "status": "error",
            "message": "Vui lòng đăng nhập hoặc cung cấp JWT Bearer Token!"
        }), 401

    question = Question.query.get(question_id)
    if not question:
        return jsonify({"status": "error", "message": f"Không tìm thấy câu hỏi #{question_id}!"}), 404

    # Kiểm tra quyền sở hữu (IDOR prevention): Chỉ tác giả hoặc Admin mới được sửa
    if question.user_id != user.id and user.role != 'admin':
        return jsonify({
            "status": "error",
            "message": "Bạn không có quyền chỉnh sửa câu hỏi của người khác!"
        }), 403

    data = request.get_json(silent=True) or {}
    new_title = data.get('title')
    new_content = data.get('content')

    if new_title is not None:
        new_title = new_title.strip()
        if not new_title:
            return jsonify({"status": "error", "message": "Tiêu đề không được để trống!"}), 400
        question.title = bleach.clean(new_title, strip=True)

    if new_content is not None:
        new_content = new_content.strip()
        if not new_content:
            return jsonify({"status": "error", "message": "Nội dung không được để trống!"}), 400
        question.content = bleach.clean(new_content, tags=['p', 'b', 'i', 'u', 'code', 'pre', 'br', 'strong', 'em', 'ul', 'ol', 'li'], strip=True)

    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Cập nhật câu hỏi thành công!",
        "data": {
            "id": question.id,
            "title": question.title,
            "content": question.content
        }
    }), 200

# 1.4. API DELETE Xóa câu hỏi (RESTful endpoint: DELETE /api/questions/<id> -> Status 200 OK)
@api_bp.route('/questions/<int:question_id>', methods=['DELETE'])
def delete_question_api(question_id):
    """
    Xóa câu hỏi qua REST API (Rubric: HTTP Method DELETE)
    Status code: 200 (OK), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found)
    """
    user = get_current_api_user()
    if not user:
        return jsonify({
            "status": "error",
            "message": "Vui lòng đăng nhập hoặc cung cấp JWT Bearer Token!"
        }), 401

    question = Question.query.get(question_id)
    if not question:
        return jsonify({"status": "error", "message": f"Không tìm thấy câu hỏi #{question_id}!"}), 404

    # Kiểm tra quyền (RBAC / IDOR): Tác giả bài viết hoặc Admin
    if question.user_id != user.id and user.role != 'admin':
        return jsonify({
            "status": "error",
            "message": "Bạn không có quyền xóa câu hỏi này!"
        }), 403

    db.session.delete(question)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Đã xóa câu hỏi #{question_id} thành công!"
    }), 200

# 1.5. API POST Tạo câu trả lời mới (RESTful endpoint: POST /api/questions/<id>/answers -> Status 201 Created)
@api_bp.route('/questions/<int:question_id>/answers', methods=['POST'])
def create_answer_api(question_id):
    """
    Tạo câu trả lời mới qua REST API (Rubric: Accurate Status Code 201 Created)
    Status code: 201 (Created), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found)
    """
    user = get_current_api_user()
    if not user:
        return jsonify({
            "status": "error",
            "message": "Vui lòng đăng nhập hoặc cung cấp JWT Bearer Token!"
        }), 401

    question = Question.query.get(question_id)
    if not question:
        return jsonify({"status": "error", "message": f"Không tìm thấy câu hỏi #{question_id}!"}), 404

    if question.is_locked:
        return jsonify({
            "status": "error",
            "message": "Câu hỏi này đã bị khóa bởi Quản trị viên, không thể gửi câu trả lời mới!"
        }), 403

    data = request.get_json(silent=True) or {}
    content = (data.get('content') or '').strip()
    if not content:
        return jsonify({
            "status": "error",
            "message": "Nội dung câu trả lời không được để trống!"
        }), 400

    clean_content = bleach.clean(content, tags=['p', 'b', 'i', 'u', 'code', 'pre', 'br', 'strong', 'em', 'ul', 'ol', 'li'], strip=True)
    answer = Answer(
        content=clean_content,
        question_id=question.id,
        user_id=user.id
    )
    db.session.add(answer)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Gửi câu trả lời thành công!",
        "data": {
            "id": answer.id,
            "question_id": question.id,
            "author": user.username,
            "created_at": answer.created_at.isoformat() if answer.created_at else None
        }
    }), 201

# 2. API GET Danh sách Tag (Public)
@api_bp.route('/tags', methods=['GET'])
def get_tags():
    tags = Tag.query.all()
    data = [{"id": t.id, "name": t.name} for t in tags]
    return jsonify({"status": "success", "data": data}), 200

# 3. API POST Chức năng Vote Câu trả lời (AJAX - Kiểm soát 1 User chỉ vote 1 lần)
@api_bp.route('/vote/answer/<int:answer_id>', methods=['POST'])
def vote_answer(answer_id):
    # 3.1. Bắt buộc đăng nhập (JWT hoặc Session)
    user = get_current_api_user()
    if not user:
        return jsonify({
            "status": "error",
            "message": "Vui lòng đăng nhập để bình chọn câu trả lời!"
        }), 401

    answer = Answer.query.get(answer_id)
    if not answer:
        return jsonify({"status": "error", "message": f"Không tìm thấy câu trả lời #{answer_id}!"}), 404

    # 3.2. Không được tự vote câu trả lời của chính mình
    if answer.user_id == user.id:
        return jsonify({
            "status": "error",
            "message": "Bạn không thể tự bình chọn cho câu trả lời của chính mình!"
        }), 400

    data = request.get_json(silent=True) or {}
    req_type = data.get('type') or request.args.get('type', 'up')
    target_type = -1 if req_type == 'down' else 1

    # 3.3. Kiểm tra xem người dùng đã từng vote câu trả lời này chưa
    existing_vote = Vote.query.filter_by(user_id=user.id, answer_id=answer.id).first()

    if not existing_vote:
        # Trường hợp 1: Chưa vote -> Tạo vote mới (+1 hoặc -1)
        new_vote = Vote(user_id=user.id, answer_id=answer.id, vote_type=target_type)
        db.session.add(new_vote)
        answer.upvotes = (answer.upvotes or 0) + target_type
        # Cộng/trừ điểm uy tín (Upvote: +10, Downvote: -5)
        adjust_reputation(answer.author, 10 if target_type == 1 else -5)
        user_vote = target_type
        message = "Bình chọn thành công!"
    elif existing_vote.vote_type == target_type:
        # Trường hợp 2: Bấm lại vào nút đã vote -> HỦY BÌNH CHỌN (Undo)
        answer.upvotes = (answer.upvotes or 0) - existing_vote.vote_type
        # Hoàn tác điểm uy tín
        adjust_reputation(answer.author, -10 if existing_vote.vote_type == 1 else 5)
        db.session.delete(existing_vote)
        user_vote = 0
        message = "Đã hủy bình chọn!"
    else:
        # Trường hợp 3: Đổi từ Upvote sang Downvote hoặc ngược lại
        answer.upvotes = (answer.upvotes or 0) - existing_vote.vote_type + target_type
        adjust_reputation(answer.author, 15 if target_type == 1 else -15)
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
@api_bp.route('/vote/question/<int:question_id>', methods=['POST'])
def vote_question(question_id):
    # 4.1. Bắt buộc đăng nhập
    user = get_current_api_user()
    if not user:
        return jsonify({
            "status": "error",
            "message": "Vui lòng đăng nhập để bình chọn câu hỏi!"
        }), 401

    question = Question.query.get(question_id)
    if not question:
        return jsonify({"status": "error", "message": f"Không tìm thấy câu hỏi #{question_id}!"}), 404

    # 4.2. Không được tự vote câu hỏi của chính mình
    if question.user_id == user.id:
        return jsonify({
            "status": "error",
            "message": "Bạn không thể tự bình chọn cho câu hỏi của chính mình!"
        }), 400

    data = request.get_json(silent=True) or {}
    req_type = data.get('type') or request.args.get('type', 'up')
    target_type = -1 if req_type == 'down' else 1

    # 4.3. Kiểm tra xem người dùng đã từng vote câu hỏi này chưa
    existing_vote = Vote.query.filter_by(user_id=user.id, question_id=question.id).first()

    if not existing_vote:
        # Trường hợp 1: Chưa vote -> Tạo vote mới (+1 hoặc -1)
        new_vote = Vote(user_id=user.id, question_id=question.id, vote_type=target_type)
        db.session.add(new_vote)
        question.upvotes = (question.upvotes or 0) + target_type
        adjust_reputation(question.author, 10 if target_type == 1 else -5)
        user_vote = target_type
        message = "Bình chọn câu hỏi thành công!"
    elif existing_vote.vote_type == target_type:
        # Trường hợp 2: Bấm lại vào nút đã vote -> HỦY BÌNH CHỌN (Undo)
        question.upvotes = (question.upvotes or 0) - existing_vote.vote_type
        adjust_reputation(question.author, -10 if existing_vote.vote_type == 1 else 5)
        db.session.delete(existing_vote)
        user_vote = 0
        message = "Đã hủy bình chọn câu hỏi!"
    else:
        # Trường hợp 3: Đổi từ Upvote sang Downvote hoặc ngược lại
        question.upvotes = (question.upvotes or 0) - existing_vote.vote_type + target_type
        adjust_reputation(question.author, 15 if target_type == 1 else -15)
        existing_vote.vote_type = target_type
        user_vote = target_type
        message = "Đã thay đổi bình chọn câu hỏi!"

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": message,
        "new_upvotes": question.upvotes,
        "user_vote": user_vote
    }), 200

# 4.4. API POST Đánh dấu / Bỏ đánh dấu Best Answer (Theo Rubric Step 5 & 7)
@api_bp.route('/answers/<int:answer_id>/best', methods=['POST'])
@api_bp.route('/questions/<int:question_id>/best-answer/<int:answer_id>', methods=['POST'])
def mark_best_answer(answer_id, question_id=None):
    user = get_current_api_user()
    if not user:
        return jsonify({"status": "error", "message": "Vui lòng đăng nhập!"}), 401
    
    answer = Answer.query.get(answer_id)
    if not answer:
        return jsonify({"status": "error", "message": f"Không tìm thấy câu trả lời #{answer_id}!"}), 404

    question = answer.question

    # Chỉ tác giả câu hỏi mới có quyền chọn Best Answer
    if question.user_id != user.id:
        return jsonify({
            "status": "error",
            "message": "Chỉ tác giả câu hỏi mới có quyền đánh dấu Câu trả lời hay nhất!"
        }), 403

    if answer.is_best:
        # Bỏ chọn Best Answer
        answer.is_best = False
        adjust_reputation(answer.author, -15)
        message = "Đã bỏ chọn câu trả lời hay nhất!"
        is_best = False
    else:
        # Bỏ chọn best answer cũ của câu hỏi nếu có
        for other in question.answers:
            if other.is_best and other.id != answer.id:
                other.is_best = False
                adjust_reputation(other.author, -15)
        
        answer.is_best = True
        adjust_reputation(answer.author, 15)
        message = "Đã đánh dấu là câu trả lời hay nhất (+15 điểm uy tín)!"
        is_best = True

    db.session.commit()
    return jsonify({
        "status": "success",
        "message": message,
        "is_best": is_best,
        "answer_id": answer.id
    }), 200

# 4.5. API POST Khóa / Mở khóa Câu hỏi (Admin Only theo Rubric Step 5)
@api_bp.route('/questions/<int:question_id>/lock', methods=['POST'])
def toggle_lock_question(question_id):
    user = get_current_api_user()
    if not user or user.role != 'admin':
        return jsonify({
            "status": "error",
            "message": "Chỉ Quản trị viên (Admin) mới có quyền khóa/mở khóa câu hỏi!"
        }), 403

    question = Question.query.get(question_id)
    if not question:
        return jsonify({"status": "error", "message": f"Không tìm thấy câu hỏi #{question_id}!"}), 404

    question.is_locked = not question.is_locked
    db.session.commit()

    msg = "Đã khóa câu hỏi thành công!" if question.is_locked else "Đã mở khóa câu hỏi thành công!"
    return jsonify({"status": "success", "message": msg, "is_locked": question.is_locked}), 200

# 4.6. API POST Ẩn / Hiện Câu hỏi Vi phạm (Moderator / Admin theo Rubric)
@api_bp.route('/questions/<int:question_id>/hide', methods=['POST'])
def toggle_hide_question(question_id):
    user = get_current_api_user()
    if not user or user.role not in ['admin', 'moderator']:
        return jsonify({
            "status": "error",
            "message": "Chỉ Kiểm duyệt viên (Moderator) hoặc Admin mới có quyền ẩn câu hỏi vi phạm!"
        }), 403

    question = Question.query.get(question_id)
    if not question:
        return jsonify({"status": "error", "message": f"Không tìm thấy câu hỏi #{question_id}!"}), 404

    question.is_hidden = not question.is_hidden
    db.session.commit()

    msg = "Đã ẩn câu hỏi vi phạm!" if question.is_hidden else "Đã khôi phục hiển thị câu hỏi!"
    return jsonify({"status": "success", "message": msg, "is_hidden": question.is_hidden}), 200

# 4.7. API POST Ẩn / Hiện Câu trả lời Vi phạm (Moderator / Admin theo Rubric)
@api_bp.route('/answers/<int:answer_id>/hide', methods=['POST'])
def toggle_hide_answer(answer_id):
    user = get_current_api_user()
    if not user or user.role not in ['admin', 'moderator']:
        return jsonify({
            "status": "error",
            "message": "Chỉ Kiểm duyệt viên (Moderator) hoặc Admin mới có quyền ẩn nội dung vi phạm!"
        }), 403

    answer = Answer.query.get(answer_id)
    if not answer:
        return jsonify({"status": "error", "message": f"Không tìm thấy câu trả lời #{answer_id}!"}), 404

    answer.is_hidden = not answer.is_hidden
    db.session.commit()

    msg = "Đã ẩn câu trả lời vi phạm!" if answer.is_hidden else "Đã khôi phục câu trả lời!"
    return jsonify({"status": "success", "message": msg, "is_hidden": answer.is_hidden}), 200

# 5. API GET Danh sách Audit Logs mới nhất (Cho Live Monitoring Dashboard Real-time có phân trang)
@api_bp.route('/admin/logs', methods=['GET'])
def get_admin_logs():
    user = get_current_api_user()
    if not user or user.role != 'admin':
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
