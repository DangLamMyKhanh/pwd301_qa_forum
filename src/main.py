import bleach
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models import db, Question, SecurityAuditLog
# from src.forms import QuestionForm (Tương lai em sẽ mở dòng này ra)

main_bp = Blueprint('main', __name__)

@main_bp.route('/ask', methods=['GET', 'POST'])
@login_required # Phải đăng nhập mới được hỏi
def ask_question():
    # form = QuestionForm()
    # if form.validate_on_submit():
    
    if request.method == 'POST':
        # ---------------------------------------------------------
        # BẢO MẬT 1: ANTI-SPAM & RATE LIMITING (Task 2.3)
        # ---------------------------------------------------------
        # Tìm câu hỏi gần nhất của User này
        last_question = Question.query.filter_by(user_id=current_user.id).order_by(Question.created_at.desc()).first()
        
        if last_question:
            # Tính thời gian từ lúc đăng câu đó đến bây giờ
            time_diff = datetime.utcnow() - last_question.created_at
            if time_diff < timedelta(minutes=1): # Nếu chưa qua 1 phút
                
                # GHI LOG VÀO DATABASE (SOC Flexing)
                log = SecurityAuditLog(
                    user_id=current_user.id,
                    ip_address=request.remote_addr,
                    action="Spam Alert: Cố tình đăng câu hỏi liên tục dưới 1 phút"
                )
                db.session.add(log)
                db.session.commit()
                
                flash("Bạn thao tác quá nhanh! Vui lòng đợi 1 phút trước khi đăng bài tiếp.", "danger")
                return redirect(url_for('main.ask_question')) # Văng ra ngoài

        # ---------------------------------------------------------
        # BẢO MẬT 2: CHỐNG XSS BẰNG BLEACH (Task 2.2)
        # ---------------------------------------------------------
        raw_content = request.form.get('content') # Lấy data thô (Có thể chứa mã độc <script>)
        
        # Nhúng vào máy giặt Bleach: Chỉ cho phép in đậm, in nghiêng, thẻ code
        allowed_tags = ['b', 'i', 'strong', 'em', 'p', 'a', 'code', 'pre']
        clean_content = bleach.clean(raw_content, tags=allowed_tags, strip=True)

        # ---------------------------------------------------------
        # LƯU VÀO DATABASE (Đã an toàn 100%)
        # ---------------------------------------------------------
        new_q = Question(
            title=request.form.get('title'),
            content=clean_content, # Lưu cái đã sạch
            user_id=current_user.id
        )
        db.session.add(new_q)
        db.session.commit()
        
        flash("Đăng câu hỏi thành công!", "success")
        return redirect(url_for('main.index'))
        
    return "<h1>Giao diện Đặt Câu Hỏi (Đợi Thành viên 1 làm)</h1>"