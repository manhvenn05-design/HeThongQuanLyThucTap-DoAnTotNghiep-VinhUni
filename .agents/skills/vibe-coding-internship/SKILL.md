---
name: vibe-coding-internship
description: >-
  Quy chuẩn và cẩm nang hướng dẫn triển khai Hệ thống quản lý thực tập & đồ án tốt nghiệp
  (Đại học Vinh) bằng Django MVT, bóc tách giao diện từ Sprint HTML sang template thân thiện với người dùng.
---

# CẨM NANG VIBE CODING: HỆ THỐNG QUẢN LÝ THỰC TẬP & ĐỒ ÁN (ĐH VINH)

Cẩm nang này định hình quy trình bóc tách giao diện, chuẩn hóa ngôn ngữ hiển thị và ánh xạ logic nghiệp vụ vào kiến trúc Django MVT theo từng Sprint.

---

## 1. QUY CHUẨN BÓC TÁCH GIAO DIỆN TỪ `Sprint_Giao_diện_Chính/`

### 1.1 Chuẩn hóa từ ngữ kỹ thuật sang ngôn ngữ người dùng (Sanitizing Technical Jargon)
Các file HTML trong thư mục `docs/Sprint_Giao_diện_Chính/` là bản dựng mẫu chứa mã kỹ thuật và ghi chú lập trình. Khi chuyển thể vào Django Templates:
* **Loại bỏ**: Toàn bộ ghi chú của dev, chú thích biến, mã mock nội bộ.
* **Bản đồ chuyển đổi mã trạng thái sang tiếng Việt thân thiện**:
  * `TRONG_DANH_SACH` → *"Trong danh sách đợt"* (Badge màu xám/xanh nhạt)
  * `CHO_XAC_NHAN` → *"Chờ GVHD tiếp nhận"* (Badge màu vàng/cam)
  * `CHO_CHOT_DE_TAI` → *"Đang chọn & chốt đề tài"* (Badge màu tím/xanh dương)
  * `DANG_THUC_HIEN` → *"Đang thực hiện"* (Badge màu xanh lá)
  * `CHAM_HUONG_DAN` → *"Chờ GVHD chấm"* (Badge màu vàng)
  * `CHO_PHAN_BIEN` → *"Chờ chấm phản biện / Hội đồng"* (Badge màu cam)
  * `HOAN_TAT` → *"Đã hoàn tất & Lưu trữ"* (Badge màu xanh lục đậm)
* **Bản đồ chuyển đổi thành phần điểm**:
  * `HUONG_DAN` → *"Điểm đánh giá GVHD"*
  * `NOI_THUC_TAP` → *"Điểm đơn vị thực tập"*
  * `PHAN_BIEN` → *"Điểm phản biện"*
  * `HOI_DONG` → *"Điểm hội đồng bảo vệ"*
  * `diem_cuoi` → *"Điểm tổng kết (hệ 10)"*

### 1.2 Phân rã cấu trúc Template (Atomic Templates)
* **`templates/base.html`**: Khung layout dùng chung (Navbar, Sidebar responsive, thông tin người dùng đang đăng nhập, thông báo Toast/Alerts, Footer).
* **`templates/components/`**: Các mảnh nhỏ tái sử dụng:
  * `stat_card.html`: Thẻ thống kê số lượng hồ sơ, tiến độ.
  * `status_badge.html`: Hiển thị nhãn trạng thái có màu sắc trực quan.
  * `filter_bar.html`: Thanh tìm kiếm, lọc theo đợt, lớp, bộ môn, GVHD.
  * `modal_confirm.html`: Hộp thoại xác nhận hành động (ví dụ: công bố danh sách, duyệt đề tài).
* **`templates/<app_name>/<sprint_view>.html`**: Màn hình chính của từng chức năng, kế thừa `base.html` và nạp dữ liệu động từ context của View.

### 1.3 Chủ động thiết kế các màn hình phụ trợ
Khi triển khai một use case, nếu giao diện chính chưa có sẵn form chi tiết:
* AI chủ động tạo trang chi tiết/form nhập liệu dựa trên hệ màu Tailwind CSS đã cấu hình trong `Sprint1.html`.
* Đảm bảo tính nhất quán: Font Nunito Sans/Public Sans, Material Symbols Outlined, bo góc `rounded-xl`, viền `border-slate-200`.

---

## 2. QUY TRÌNH THỰC HIỆN TỪNG SPRINT (SOP)

Mỗi Sprint bắt buộc tuân theo 6 bước:

```text
1. Định nghĩa Models -> 2. Migration -> 3. Đăng ký Admin
        ↓
4. Viết Services & Selectors -> 5. Tạo Views & Templates -> 6. Kiểm tra & Báo cáo
```

### Chi tiết các bước:
1. **Bước 1 (Models)**: Viết các class trong `models.py` khớp 100% với tài liệu CSDL (tên trường, kiểu dữ liệu, quan hệ khóa ngoại, `on_delete`, `choices`).
2. **Bước 2 (Migration)**:
   * Chạy: `python manage.py makemigrations`
   * Chạy: `python manage.py migrate`
   * Mở SQLite Viewer kiểm tra bảng vừa tạo.
3. **Bước 3 (Admin)**: Đăng ký model vào `admin.py` với `list_display`, `list_filter`, `search_fields` để có thể xem/sửa nhanh dữ liệu demo.
4. **Bước 4 (Services & Selectors)**:
   * `selectors.py`: Viết các hàm lọc dữ liệu an toàn theo người dùng (`for_user`, theo khoa, theo vai trò).
   * `services.py`: Viết nghiệp vụ, kiểm tra ràng buộc quyền hạn, chuyển trạng thái vòng đời.
5. **Bước 5 (Views & Templates)**:
   * Viết View kết nối service/selector.
   * Chuyển thể HTML mẫu từ thư mục `docs/Sprint_Giao_diện_Chính/` sang Template động.
   * Thay thế văn bản mẫu thô bằng cú pháp Django `{{ variable }}`, vòng lặp `{% for %}`, thẻ điều kiện `{% if %}`.
6. **Bước 6 (Kiểm tra)**:
   * Chạy `python manage.py check`.
   * Bật server chạy thử màn hình trên trình duyệt.
   * Báo cáo kết quả và xác nhận từ người dùng trước khi chuyển sang Sprint tiếp theo.

---

## 3. CHECKLIST KIỂM TRA TRƯỚC KHI KẾT THÚC MỘT SPRINT

- [ ] Tên bảng và tên trường trong code khớp hoàn toàn với `CSDL_He_thong_quan_ly_thuc_tap_Markdowfile.md`.
- [ ] Không có chuỗi mã enum thô (như `CHO_XAC_NHAN`, `HUONG_DAN`) hiển thị trực tiếp trước mắt người dùng trên giao diện.
- [ ] Mọi thay đổi trạng thái đều đi qua `services.chuyen_trang_thai_*`.
- [ ] Không có mật khẩu hoặc điểm số nhạy cảm bị rò rỉ trong log hay view sinh viên.
- [ ] `python manage.py check` trả về **0 issues**.
- [ ] Template kế thừa hoàn chỉnh từ `base.html` và hiển thị mượt mà trên trình duyệt.
