from flask import Blueprint, jsonify

# Khởi tạo Blueprint có tên là 'api', tất cả các link tự động thêm tiền tố '/api'
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/test')
def api_test():
    # API thì trả về chuỗi JSON chứ không trả về HTML
    return jsonify({"status": "success", "message": "API Blueprint hoạt động tốt!"})