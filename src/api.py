from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, Question, Tag, Answer

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 1. API GET Danh sách Câu hỏi (Public)
@api_bp.route('/questions', methods=['GET'])
def get_questions():
    questions = Question.query.order_by(Question.created_at.desc()).all()
    # Chuyển dữ liệu Python thành JSON
    data = []
    for q in questions:
        data.append({
            "id": q.id,
            "title": q.title,
            "views": q.views,
            "author": q.author.username
        })
    return jsonify({"status": "success", "data": data}), 200

# 2. API GET Danh sách Tag (Public)
@api_bp.route('/tags', methods=['GET'])
def get_tags():
    tags = Tag.query.all()
    data = [{"id": t.id, "name": t.name} for t in tags]
    return jsonify({"status": "success", "data": data}), 200

# 3. API POST Chức năng Vote (BẢO MẬT: Bắt buộc có Token)
@api_bp.route('/vote/answer/<int:answer_id>', methods=['POST'])
@jwt_required()  # <--- BẢO VỆ BẰNG JWT! KHÔNG CÓ TOKEN LÀ BỊ ĐÁ VĂNG
def vote_answer(answer_id):
    # Lấy ID của user đang đăng nhập từ Token
    current_user_id = get_jwt_identity()
    
    answer = Answer.query.get_or_404(answer_id)
    answer.upvotes += 1 # Cộng 1 điểm
    db.session.commit()
    
    return jsonify({
        "status": "success", 
        "message": "Vote thành công!", 
        "new_upvotes": answer.upvotes
    }), 200