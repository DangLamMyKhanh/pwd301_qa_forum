from flask_login import LoginManager

# Khởi tạo LoginManager quản lý phiên đăng nhập
login_manager = LoginManager()

# Cấu hình LoginManager: Nếu chưa đăng nhập mà cố vào trang cấm, sẽ bị cho về đây
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này!'
login_manager.login_message_category = 'warning'
