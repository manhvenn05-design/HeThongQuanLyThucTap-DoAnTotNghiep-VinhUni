# NHẬT KÝ BÀN GIAO & PHÁT TRIỂN HỆ THỐNG
> **Dự án**: Hệ thống Quản lý Thực tập & Đồ án tốt nghiệp — Trường Kỹ thuật và Công nghệ, Đại học Vinh  
> **Cập nhật lúc**: 09:38 Ngày 09/11/2026  
> **Tài liệu căn cứ tối cao**: `GEMINI.md`, `docs/Mô Tả Dự Án.md`, `docs/CSDL_He_thong_quan_ly_thuc_tap_Markdowfile.md`

---

## 1. TỔNG QUAN TÌNH TRẠNG HỆ THỐNG
* **Kiến trúc**: Django MVT phân tầng (`models.py`, `services.py`, `selectors.py`, `views.py`, `forms.py`).
* **Cơ sở dữ liệu**: Đầy đủ 32 bảng chuẩn `snake_case` tiếng Việt không dấu.
* **Hạ tầng kiểm thử**:
  * `python manage.py check`: **0 lỗi (0 silenced)**.
  * `python manage.py test`: **11/11 test cases PASSED** (Bao gồm bộ kiểm thử bảo mật & liêm chính dữ liệu).
  * `Django Client HTTP Smoke Test`: **30/30 endpoints đạt HTTP 200 OK**.

---

## 2. KẾT QUẢ DỌN DẸP & TINH CHỈNH GIAO DIỆN (PHIÊN 09/11/2026)

### A. Dọn dẹp tệp thừa & Tối ưu dung lượng
1. **Giải phóng 14.70 MB ảnh thừa trong `static/images/`**:
   * Đã xóa sạch 10 tệp ảnh thử nghiệm kích thước lớn không còn sử dụng.
   * Thư mục `static/images/` hiện chỉ lưu trữ 2 tệp tài nguyên chính thức duy nhất:
     * `logo_vinhuni.png` (Logo tròn chính thức Trường Đại học Vinh 1959).
     * `trong_dong_gold_champagne.png` (Trống đồng Vàng Champagne Hoàng Kim `#E8CA8A`).
   * Đồng bộ 100% template dùng `{% static 'images/logo_vinhuni.png' %}` theo đúng quy định tại `GEMINI.md`.
2. **Dọn dẹp tệp tải lên tạm thời & Bổ sung `.gitignore`**:
   * Dọn sạch các tệp Excel upload test cũ trong `media/excel_imports/`.
   * Tạo tệp `.gitignore` chuẩn cho dự án Django, bảo vệ kho mã nguồn khỏi file rác và cache.

### B. Loại bỏ triệt để lỗi giao diện nghiệp dư & Phong cách AI (AI Artifacts Cleaned)
1. **Thay thế toàn bộ 35 popup `alert()` bằng Toast Notification học thuật (`showToast`)**:
   * Xóa bỏ hoàn toàn các lệnh `alert(...)` thô thiển của trình duyệt ở Cổng Giảng viên, Cổng Sinh viên và các Dashboard.
   * Tích hợp **Hệ thống Toast Notification học thuật** trên `templates/base.html`: Tự động trượt lên ở góc dưới màn hình, có icon, tiêu đề trang trọng, thông báo chi tiết và tự đóng sau 4 giây.
2. **Chuẩn hóa thuật ngữ học thuật (Academic Phrasing)**:
   * Bỏ cụm từ tiếng Anh `"Snake-draft"` trên giao diện: Đổi thành `"Gợi ý phân bổ cân bằng GPA"` hoặc `"Thuật toán phân bổ ziczac cân bằng theo điểm GPA"`.
   * Badge phương thức phân bổ được chuẩn hóa từ `"Snake"` và `"Ghép tay"` thành `"Tự động"` và `"Chỉ định"`.
   * Màn hình Đăng nhập: Bỏ nhãn `"Tài khoản thử nghiệm nhanh (1-Click)"`, đổi thành `"Đăng nhập nhanh theo vai trò"`.
3. **Sửa lỗi cấu trúc HTML / Dangling Block**:
   * Phát hiện và xóa bỏ khối mã thẻ lặp đề tài gợi ý thừa (dangling block) ngoài thẻ `{% endif %}` trong `lecturer_portal.html`.
   * Chuẩn hóa tên hàm chuyển tab trong `templates/sprint5/dashboard.html` thành `switchGradingTab`.

### C. Bộ chọn đợt học thuật (Academic Batch Switcher) & Bảo mật dữ liệu
1. **Cấu trúc 3 tầng chuẩn quy chế đại học**:
   * Phân cấp: **Năm học $\rightarrow$ Học kỳ $\rightarrow$ Đợt (Chính khóa / Bổ sung)**.
   * Bộ chọn đợt toàn cục trên thanh Topbar ghi nhớ qua Session (`active_dot_id`).
   * Tự động kích hoạt **Chế độ Chỉ xem (Read-only)** kèm banner thông báo khi người dùng chuyển sang xem các đợt lưu trữ lịch sử (`HOAN_TAT`).
2. **Bảo mật & Liêm chính CSDL**:
   * Điểm GPA (`diem_dau_vao`) chỉ duy nhất Trưởng khoa được xem (đã ẩn khỏi Sinh viên và Giảng viên).
   * Ràng buộc Giảng viên phản biện khác GVHD (`GVPB != GVHD`) được thực thi ở tầng model `clean()`.
   * Điểm đã gửi (`DA_GUI`) bất biến, không thể sửa khi chưa có lệnh mở lại từ Trưởng khoa.
   * Chuyển trạng thái tập trung duy nhất qua `core.state`.
