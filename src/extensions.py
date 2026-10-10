from flask_bcrypt import Bcrypt # cung cấp các hàm để hash mật khẩu, khi user đăng kí tài khoản thì password sẽ bị mã hóa trước khi đưa vào database
from flask_login import LoginManager

# Khởi tạo các công cụ bảo mật
bcrypt = Bcrypt()
login_manager = LoginManager()

# Cấu hình LoginManager: Nếu chưa đăng nhập mà cố vào trang cấm, sẽ bị cho về đây
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này!'
login_manager.login_message_category = 'warning'