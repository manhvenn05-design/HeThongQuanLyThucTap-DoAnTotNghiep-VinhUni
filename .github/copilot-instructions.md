# COPILOT & CODEX INSTRUCTIONS — HỆ THỐNG QUẢN LÝ THỰC TẬP & ĐỒ ÁN (ĐH VINH)

> **Dành cho VS Code Codex / GitHub Copilot**: Bạn đang làm việc trên dự án Django MVT phân tầng của Trường ĐH Vinh.
> Mọi tác vụ lập trình của bạn PHẢI tuân thủ 100% các chỉ dẫn dưới đây để đồng bộ tuyệt đối với Antigravity.

---

## 1. HÀNH ĐỘNG BẮT BUỘC ĐẦU TIÊN
Trước khi viết bất kỳ đoạn code nào:
1. Đọc file `AGENT_CONTEXT.md` tại thư mục gốc để nắm:
   - Nhánh Git hiện tại và Sprint đang làm việc.
   - Các use case đã hoàn thành (không làm lại).
   - Checklist use case tiếp theo cần triển khai.
2. Kiểm tra môi trường:
   - Dùng lệnh: `.\.venv\Scripts\python.exe manage.py check` (phải 0 lỗi).
   - Python virtualenv: `.\.venv\Scripts\python.exe`.

---

## 2. NGUYÊN TẮC BẤT DI BẤT DỊCH (RULE OF LAW)
1. **CSDL 32 bảng chuẩn**:
   - Đối chiếu chính xác `docs/CSDL_He_thong_quan_ly_thuc_tap_Markdowfile.md`.
   - Tuyệt đối không tự ý đổi tên bảng, tên cột, đổi kiểu dữ liệu. Tên viết bằng tiếng Việt không dấu, `snake_case`.
2. **Dịch vụ chuyển trạng thái duy nhất (Single State Transition Service)**:
   - Mọi thay đổi trạng thái của đợt (`dot`) và hồ sơ (`ho_so`) bắt buộc gọi qua:
     `core.state.chuyen_trang_thai_dot` và `core.state.chuyen_trang_thai_ho_so`.
   - Tuyệt đối KHÔNG gọi `.update(trang_thai=...)` trực tiếp trong views.
3. **Bảo mật điểm GPA đầu vào (`diem_dau_vao`)**:
   - CHỈ DUY NHẤT Trưởng khoa có quyền xem. Không để lộ ra giao diện Giảng viên hay Sinh viên.
4. **Liêm chính điểm số**:
   - Sinh viên KHÔNG ĐƯỢC nhập hay sửa điểm.
   - Giảng viên phản biện KHÔNG ĐƯỢC TRÙNG với GVHD của cùng một hồ sơ.
5. **Cấu hình trọng số điểm (`dot_trong_so`)**:
   - Tổng tỷ trọng % các thành phần điểm của một đợt bắt buộc bằng đúng 100%.
6. **Nhật ký hệ thống (`nhat_ky_he_thong`)**:
   - Ghi hành vi tác động, KHÔNG ghi giá trị điểm số vào log.
7. **Ngôn ngữ giao diện**:
   - Chuẩn hóa 100% tiếng Việt trang trọng, học thuật cho người dùng thật. Không để lộ tên enum (`CHO_CHOT`, `PHAN_CONG`, `DA_CHOT`...) ra màn hình.
   - Logo: Sử dụng `{% static 'images/logo_vinhuni.png' %}`.

---

## 3. KIẾN TRÚC PHÂN TẦNG (DJANGO MVT)
- **`models.py`**: Chỉ chứa cấu trúc dữ liệu và constraints.
- **`services.py`**: Chứa toàn bộ logic nghiệp vụ, thuật toán, validation.
- **`selectors.py`**: Chứa toàn bộ câu truy vấn phân quyền theo vai trò/khoa.
- **`views.py`**: View mỏng, chỉ nhận request, gọi selectors/services và redirect kèm messages hoặc render template.
- **`templates/`**: Kế thừa `base.html`, dùng Tailwind CSS.

---

## 4. KHI KẾT THÚC PHIÊN LÀM VIỆC (HANDOFF BÀN GIAO CHO ANTIGRAVITY)
Trước khi kết thúc phiên:
1. Chạy kiểm thử:
   - `.\.venv\Scripts\python.exe manage.py check`
   - `.\.venv\Scripts\python.exe manage.py test` (Đảm bảo 100% tests PASS).
2. Cập nhật file `AGENT_CONTEXT.md`:
   - Ghi nhận trạng thái mới nhất, số test case đã pass.
   - Tick vào checklist các công việc đã làm xong.
   - Viết mục `GHI CHÚ PHIÊN LÀM VIỆC CUỐI` để Antigravity đọc và tiếp tục.
3. Commit và push Git:
   - `git add .`
   - `git commit -m "feat/fix: mô tả nội dung"`
   - `git push origin <nhánh-hiện-tại>`
