# ProjectA - Python Django MVT (Vibe Coding Ready)

Dự án được chuẩn bị sẵn sàng cho quy trình **Vibe Coding** với kiến trúc **Django MVT (Model - View - Template)**, tích hợp sẵn sàng với thiết kế từ **Google Stitch** thông qua MCP.

---

## 1. Cấu trúc thư mục (Django MVT)

```text
ProjectA/
├── .venv/                  # Môi trường ảo Python 3.12 (đã cài Django, dotenv, requests)
├── config/                 # Cấu hình dự án Django
│   ├── settings.py         # Thiết lập (đã nạp .env, kết nối templates, static, SQLite)
│   ├── urls.py             # Định tuyến URL
│   ├── wsgi.py / asgi.py
├── templates/              # Thư mục Template (chứa base.html & nơi đổ UI từ Stitch)
│   └── base.html           # Khung layout chuẩn (Tailwind CSS CDN + Django blocks)
├── static/                 # Thư mục Static files
│   ├── css/style.css
│   └── js/main.js
├── .env                    # Biến môi trường (SECRET_KEY, STITCH credentials)
├── .env.example
├── .gitignore
├── db.sqlite3              # Database SQLite (đã migrate sẵn auth & sessions)
├── manage.py
├── requirements.txt        # Danh sách thư viện Python
└── STITCH_MCP_GUIDE.md     # Hướng dẫn kết nối Google Stitch MCP
```

---

## 2. Lựa chọn Database cho Vibe Coding

| Database | Đánh giá cho Vibe Coding | Khuyến nghị |
| :--- | :--- | :--- |
| **SQLite (Đang kích hoạt)** | ⭐⭐⭐⭐⭐ **Tối ưu nhất**: Zero-config, lưu thành 1 file `db.sqlite3`. Cực nhanh để thử nghiệm, xóa làm lại, rollback migration khi vibe code. | **Nên dùng ngay** trong giai đoạn dựng prototype & vibe coding. |
| **PostgreSQL** | ⭐⭐⭐⭐ **Production standard**: Thích hợp khi deploy thực tế lên cloud (Railway, Render, AWS). | Chỉ cần đổi 1 dòng config `DATABASES` trong `settings.py` khi dự án hoàn thiện. |

---

## 3. Lệnh khởi chạy nhanh

Kích hoạt server phát triển:

```powershell
# Từ thư mục C:\Users\Admin\Documents\ProjectA:
.\.venv\Scripts\python.exe manage.py runserver
```
Truy cập: `http://127.0.0.1:8000/`
