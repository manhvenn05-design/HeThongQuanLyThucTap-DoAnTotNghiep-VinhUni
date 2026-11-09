# QUY TẮC PHÁT TRIỂN DỰ ÁN: HỆ THỐNG QUẢN LÝ THỰC TẬP & ĐỒ ÁN TỐT NGHIỆP
> **Đơn vị**: Trường Kỹ thuật và Công nghệ – Đại học Vinh  
> **Kiến trúc**: Django MVT (Monolithic phân tầng) | **CSDL**: SQLite (Dev/Vibe) → PostgreSQL (Prod)  
> **Tài liệu nguồn sự thật**: `docs/Mô Tả Dự Án.md` và `docs/CSDL_He_thong_quan_ly_thuc_tap_Markdowfile.md`

Mọi AI Agent khi làm việc trên kho mã nguồn này **BẮT BUỘC** tuân thủ 100% các điều khoản dưới đây:

---

## 1. NGUYÊN TẮC BẤT DI BẤT DỊCH (KHÔNG ĐƯỢC VI PHẠM)

1. **Tuân thủ tuyệt đối danh mục Use Case**:
   * Chỉ phát triển trong phạm vi **31 use case (UC01 – UC31)** được đặc tả trong `docs/Mô Tả Dự Án.md`.
   * Tuyệt đối không tự ý vẽ thêm tính năng nằm ngoài phạm vi (như email, SMS, mobile app riêng,...).
2. **Tuân thủ tuyệt đối cấu trúc CSDL 32 bảng**:
   * Không đổi tên bảng, không đổi tên cột, không tự ý thêm bớt trường hay thay đổi giá trị enum.
   * Tên bảng và tên cột viết bằng tiếng Việt không dấu, dạng `snake_case` chuẩn 100% theo tài liệu `docs/CSDL_He_thong_quan_ly_thuc_tap_Markdowfile.md`.
3. **Bảo mật & Liêm chính dữ liệu**:
   * **Không lưu mật khẩu** của cổng sinh viên USMART ở bất kỳ đâu (CSDL, log, session).
   * **Sinh viên tuyệt đối không được nhập hoặc sửa điểm**.
   * Điểm trung bình đầu vào (`diem_dau_vao`) **chỉ Trưởng khoa** có quyền xem.
   * Giảng viên phản biện **không được trùng** với GVHD của cùng một hồ sơ (`ho_so`).
   * Điểm đã gửi (`DA_GUI`) và hồ sơ đã hoàn tất (`HOAN_TAT`) không thể chỉnh sửa nếu không có lệnh mở lại từ Trưởng khoa.
   * Nhật ký hệ thống (`nhat_ky_he_thong`) chỉ ghi hành vi tác động, **không ghi giá trị điểm số**.
4. **Dịch vụ chuyển trạng thái duy nhất (Single State Transition Service)**:
   * Mọi sự thay đổi trạng thái của `dot` (6 trạng thái) và `ho_so` (7 trạng thái) bắt buộc phải gọi thông qua **một hàm dịch vụ tập trung duy nhất** trong `services.py` (ví dụ: `chuyen_trang_thai_ho_so`). Tuyệt đối không gọi `.update(trang_thai=...)` rải rác trong views.

---

## 2. PHÂN TẦNG KIẾN TRÚC DJANGO

Mỗi ứng dụng (app) Django trong dự án phải tuân thủ chặt chẽ cấu trúc phân tầng sau:
* **`models.py`**: Chỉ định nghĩa cấu trúc dữ liệu, quan hệ khóa ngoại và ràng buộc (constraints). Đầy đủ `verbose_name`, `__str__`.
* **`services.py`**: Chứa **toàn bộ logic nghiệp vụ** (chuyển trạng thái, thuật toán chia đều sinh viên, tính điểm trung bình có trọng số, bóc tách file Excel,...).
* **`selectors.py`**: Chứa các hàm truy vấn dữ liệu có kiểm tra phạm vi quyền (`for_user`, lọc theo `khoa_id`, theo vai trò HD, PB, HĐ). View không viết query phức tạp.
* **`views.py`**: Tầng view mỏng. Chỉ nhận request, gọi `selectors`/`services` và render template hoặc trả về partial HTML (HTMX).
* **`forms.py`**: Validate dữ liệu đầu vào từ người dùng.
* **`templates/`**: Chứa giao diện MVT.

---

## 3. TIÊU CHUẨN GIAO DIỆN & BÓC TÁCH TEMPLATES

1. **Ngôn ngữ người dùng thật (User-Friendly UI)**:
   * Giao diện mẫu trong `docs/Sprint_Giao_diện_Chính/` có thể chứa từ ngữ kỹ thuật, tên mã enum của CSDL hoặc các ghi chú cho lập trình viên.
   * **Khi đưa vào Template**: Phải chuẩn hóa toàn bộ thành **tiếng Việt tự nhiên, trang trọng, thân thiện với người dùng thực tế** (Trưởng khoa, Giảng viên, Sinh viên).
   * Ví dụ: 
     * `CHO_CHOT` → Hiển thị badge: *"Chờ GVHD duyệt"*.
     * `HUONG_DAN` → *"Điểm đánh giá GVHD"*.
     * `NOI_THUC_TAP` → *"Điểm đơn vị thực tập"*.
     * Xóa bỏ hoàn toàn các ghi chú nội bộ của dev trong giao diện thật.
2. **Kế thừa Layout chung (`templates/base.html`)**:
   * Sử dụng thống nhất hệ thống font chữ: `Nunito Sans`, `Public Sans` và icon `Material Symbols Outlined`.
   * Sử dụng Tailwind CSS v3 để dựng layout nhất quán với mẫu sprint.
   * Tách nhỏ các component dùng chung (navbar, sidebar, modal, pagination) vào `templates/components/`.
3. **Chủ động tạo màn hình phụ trợ**:
   * Các file sprint (`Sprint1.html` → `Sprint6.html`) chỉ là màn hình bảng điều khiển chính.
   * AI phải chủ động thiết kế thêm các màn hình chi tiết, form nhập liệu, popup xác nhận theo đúng ngôn ngữ thiết kế (design language) của Sprint tương ứng khi triển khai từng use case.
4. **Logo chuẩn của Trường Đại học Vinh**:
   * Mọi màn hình/template khi hiển thị logo bắt buộc sử dụng ảnh: `{% static 'images/logo_vinhuni.png' %}` (Logo tròn chính thức của Trường Đại học Vinh - Vinh University 1959).

---

## 4. QUY TRÌNH PHÁT TRIỂN THEO SPRINT (NO JUMPING)

Dự án được triển khai tuần tự theo 6 Sprint tương ứng với vòng đời đợt thực tập/đồ án:
* **Sprint 1 (Chuẩn bị)**: UC03, UC04, UC05, UC06 (`CHUAN_BI`).
* **Sprint 2 (Phân công)**: UC07, UC08, UC09, UC10, UC11 (`PHAN_CONG`).
* **Sprint 3 (Chốt đề tài)**: UC12, UC13, UC14, UC15 (`CHOT_DE_TAI`).
* **Sprint 4 (Thực hiện)**: UC16, UC17, UC18, UC31 (`THUC_HIEN`).
* **Sprint 5 (Chấm điểm)**: UC19, UC20, UC21, UC22, UC23, UC24 (`CHAM_DIEM`).
* **Sprint 6 (Hoàn tất)**: UC25, UC26, UC27 (`HOAN_TAT`).

**Kỷ luật mỗi bước**:
1. Chỉ làm dứt điểm từng Sprint. Không làm dở dang hoặc nhảy cóc sang Sprint khác.
2. Tạo/cập nhật Model -> Chạy `makemigrations` & `migrate` -> Đăng ký Django Admin -> Viết Services/Selectors -> Tạo View & Template -> Chạy `manage.py check` đạt 0 lỗi -> Kiểm tra trực quan -> Được người dùng xác nhận mới chuyển sang Sprint tiếp theo.
