# 1. Kéo base image Python 3.11 chính thức 
FROM python:3.11-slim

# Thiết lập các biến môi trường cho Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000

# 2. Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Cài đặt các công cụ hệ thống tối thiểu cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 3. Copy file requirements.txt trước để tận dụng Docker cache
COPY requirements.txt /app/

# Nâng cấp pip và cài đặt toàn bộ thư viện của dự án
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4. Copy toàn bộ mã nguồn vào container
COPY . /app/

# 5. Mở cổng 5000 cho ứng dụng Flask
EXPOSE 5000

# 6. Khởi chạy ứng dụng Flask
CMD ["python", "app.py"]
