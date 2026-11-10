# 1. Tải code về
git clone <link-repo>
cd <ten-repo>

# 2. Tạo môi trường ảo
python -m venv .venv
.\.venv\Scripts\activate   # (hoặc source .venv/bin/activate trên Mac/Linux)

# 3. Cài đặt thư viện
pip install -r requirements.txt

# 4. Tạo file cấu hình môi trường
copy .env.example .env

# 5. Tạo bảng CSDL và nạp sẵn 26 tài khoản thử nghiệm
python manage.py migrate
python manage.py loaddata fixtures/seed_data.json

# 6. Khởi chạy
python manage.py runserver
