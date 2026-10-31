"""
view_logs.py - Xem danh sách Security Audit Logs trực tiếp từ Terminal.

Chạy: python view_logs.py
"""
import sys
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

from app import app
from src.models import db, SecurityAuditLog, User

def show_logs(limit=30):
    with app.app_context():
        logs = SecurityAuditLog.query.order_by(SecurityAuditLog.timestamp.desc()).limit(limit).all()
        users_map = {u.id: u.username for u in User.query.all()}

        print("=" * 80)
        print(f"DANH SÁCH {len(logs)} SECURITY AUDIT LOGS GẦN NHẤT")
        print("=" * 80)

        if not logs:
            print("Chưa có log bảo mật nào trong Database.")
            return

        header = f"{'ID':<6} | {'THỜI GIAN':<19} | {'IP ADDRESS':<15} | {'USER':<12} | {'HÀNH ĐỘNG'}"
        print(header)
        print("-" * 80)

        for l in logs:
            uname = users_map.get(l.user_id, "Guest") if l.user_id else "Guest"
            time_str = l.timestamp.strftime('%Y-%m-%d %H:%M:%S') if l.timestamp else "N/A"
            print(f"{l.id:<6} | {time_str:<19} | {l.ip_address:<15} | {uname:<12} | {l.action}")

        print("=" * 80)

if __name__ == "__main__":
    show_logs()

