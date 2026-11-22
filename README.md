# HỆ THỐNG QUẢN LÝ THỰC TẬP & ĐỒ ÁN TỐT NGHIỆP
> **Đơn vị đào tạo**: Trường Kỹ thuật và Công nghệ – Đại học Vinh (Vinh University 1959)  
> **Kiến trúc phát triển**: Django MVT Phân tầng (Layered Architecture: `models` - `services` - `selectors` - `views` - `templates`)  
> **Cơ sở dữ liệu**: SQLite (Môi trường Dev) $\rightarrow$ PostgreSQL (Môi trường Production)

---

## 1. GIỚI THIỆU TỔNG QUAN

Hệ thống được xây dựng nhằm số hóa toàn diện quy trình tổ chức, theo dõi và đánh giá thực tập & đồ án tốt nghiệp cho sinh viên:
- **Phạm vi nghiệp vụ**: 31 Use Case cốt lõi (UC01 – UC31), trải qua 6 giai đoạn vòng đời (Sprint 1 đến Sprint 6).
- **Mô hình CSDL**: Chuẩn hóa 32 bảng liên kết chặt chẽ theo đặc tả đào tạo của nhà trường.
- **Phân quyền vai trò (Role-Based Access Control)**:
  - 🎓 **Trưởng khoa**: Mở đợt, cấu hình thời lượng đợt, duyệt danh sách, giám sát toàn khóa.
  - 👨‍🏫 **Giảng viên**: Ba vai trò độc lập (Hướng dẫn, Phản biện, Hội đồng bảo vệ).
  - 👨‍🎓 **Sinh viên**: Đăng ký đề tài, nộp minh chứng, theo dõi tiến độ và điểm số.

---

## 2. HƯỚNG DẪN CÀI ĐẶT NHANH CHO THÀNH VIÊN TRONG NHÓM (GETTING STARTED)

Dành cho các thành viên trong nhóm khi vừa tải (clone) mã nguồn về máy:

### Bước 1: Tải mã nguồn về máy
```bash
git clone https://github.com/<tai-khoan>/<ten-repo>.git
cd <ten-repo>
```

### Bước 2: Khởi tạo & Kích hoạt Môi trường ảo (Python Virtual Environment)
* **Trên hệ điều hành Windows (PowerShell / Git Bash)**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\activate
  ```
* **Trên hệ điều hành macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Bước 3: Cài đặt danh sách thư viện bắt buộc
```bash
pip install -r requirements.txt
```

### Bước 4: Thiết lập file cấu hình môi trường (.env)
Tạo file `.env` từ mẫu `.env.example`:
* **Windows**:
  ```powershell
  copy .env.example .env
  ```
* **macOS / Linux**:
  ```bash
  cp .env.example .env
  ```

### Bước 5: Đồng bộ Cơ sở dữ liệu & Nạp dữ liệu mẫu (Seed Data)
Chạy lần lượt 2 lệnh sau để tạo bảng CSDL và nạp sẵn 26 tài khoản người dùng cùng 4 đợt mẫu:
```bash
python manage.py migrate
python manage.py loaddata fixtures/seed_data.json
```

### Bước 6: Khởi chạy máy chủ phát triển
```bash
python manage.py runserver
```
👉 Mở trình duyệt truy cập: **`http://127.0.0.1:8000/`** (Hệ thống sẽ hiển thị ngay màn hình Đăng nhập học thuật).

---

## 3. DANH SÁCH TÀI KHOẢN ĐĂNG NHẬP THỬ NGHIỆM

Hệ thống đã có sẵn tài khoản mẫu cho từng vai trò với **mật khẩu chung là: `123456`**:

| Vai trò | Tên đăng nhập | Mã định danh cán bộ / MSSV | Quyền hạn & Cổng truy cập |
| :--- | :--- | :--- | :--- |
| **Trưởng khoa** | `truongkhoa` | `CB_TK01` | Toàn quyền quản trị đợt, mở đợt, phân công (`/sprint1/`) |
| **Giảng viên** | `gv_nguyenvanan` | `CB_GV01` | Cổng tác nghiệp GV: Hướng dẫn, Phản biện, Hội đồng (`/giangvien/`) |
| **Sinh viên** | `sv_hoanglong` | `211108234` | Cổng tác nghiệp SV: Nộp đề tài, báo cáo tuần (`/sinhvien/`) |
| **Quản trị viên** | `admin` | - | Trang quản trị hệ thống Django Admin (`/admin/`) |

---

## 4. QUY TRÌNH LÀM VIỆC NHÓM & QUY TẮC NHÁNH (GIT BRANCHING STRATEGY)

Để làm việc nhóm hiệu quả, **tuyệt đối không bị xung đột (Merge Conflict)**, nhóm cần tuân thủ nghiêm ngặt các quy tắc sau:

### 1. Phân chia nhánh (Branching Rule)
- Nhánh `main`: **Nhánh thiêng liêng**, chỉ chứa mã nguồn đã kiểm tra chạy mượt mà, đạt 0 lỗi (`python manage.py check`). **Không ai được code hoặc commit trực tiếp vào `main`**.
- Mỗi thành viên khi nhận một nhiệm vụ/Use Case bắt buộc phải tạo một nhánh mới từ `main` theo quy tắc đặt tên:
  * `feature/sprint1-uc03-presets` (Làm tính năng cấu hình đợt)
  * `feature/sprint1-uc04-excel` (Làm tính năng bóc tách Excel)
  * `feature/sprint2-uc08-allocation` (Làm thuật toán phân công)
  * `fix/ten-loi-can-sua` (Nhánh sửa lỗi)

### 2. Quy trình làm việc hàng ngày của mỗi thành viên
```bash
# Bước 1: Cập nhật code mới nhất từ main về máy trước khi làm việc
git checkout main
git pull origin main

# Bước 2: Tạo nhánh riêng của mình để làm tính năng
git checkout -b feature/sprint1-uc03-presets

# Bước 3: Viết code và kiểm tra kỹ lưỡng (Kiểm tra 0 lỗi)
python manage.py check
python manage.py test

# Bước 4: Lưu vết thay đổi
git add .
git commit -m "feat(dots): Hoan thien luu cau hinh 4 presets vao CSDL"

# Bước 5: Đẩy nhánh riêng của mình lên GitHub
git push -u origin feature/sprint1-uc03-presets
```

### 3. Hợp nhất code (Pull Request & Merge)
1. Lên GitHub, bấm nút **"Compare & pull request"**.
2. Mô tả rõ những file mình vừa sửa, tính năng mình vừa thêm.
3. Trưởng nhóm (hoặc bạn cùng nhóm) kiểm tra code, nếu chạy tốt $\rightarrow$ Bấm **"Merge pull request"** để gộp vào `main`.
4. Sau khi merge xong, các thành viên khác chỉ cần gõ `git checkout main && git pull origin main` là có đầy đủ code mới nhất của bạn!

---

## 5. NGUYÊN TẮC VÀNG TRÁNH XUNG ĐỘT CODE (MERGE CONFLICT)

1. **Phân chia theo App / File rõ ràng**:
   - Người làm việc với app `dots` thì chỉ sửa các file trong thư mục `dots/`.
   - Người làm việc với app `hoso` thì chỉ sửa các file trong `hoso/`.
   - Tránh việc 2 người cùng sửa chung 1 file template hoặc 1 file view cùng một lúc.
2. **Kỷ luật kiến trúc MVT phân tầng**:
   - Luôn đặt logic nghiệp vụ vào `services.py`.
   - Luôn đặt câu lệnh truy vấn vào `selectors.py`.
   - View (`views.py`) phải giữ thật mỏng, chỉ nhận request và trả về kết quả.
3. **Tuyệt đối không đẩy file rác lên GitHub**:
   - Không đẩy `.env` (chứa khóa bí mật).
   - Không đẩy thư mục ảo `.venv/` hoặc file `db.sqlite3`.
   - Chỉ lưu và cập nhật dữ liệu chung qua file `fixtures/seed_data.json`.
