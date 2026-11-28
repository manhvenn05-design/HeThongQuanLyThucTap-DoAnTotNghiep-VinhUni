---
name: hybrid-workflow
description: >-
  Quy chuẩn bắt buộc cho AI (Antigravity & VS Code Codex) khi phát triển dự án Hệ thống quản lý thực tập & đồ án tốt nghiệp (Đại học Vinh).
  Đảm bảo 100% tính nhất quán về kiến trúc Django MVT, bảo mật dữ liệu, quy trình bàn giao (handoff) qua AGENT_CONTEXT.md và kỷ luật kiểm thử.
---

# QUY CHUẨN BẮT BUỘC CHO AI: ANTIGRAVITY & VS CODE CODEX (HYBRID WORKFLOW)

Tài liệu này là **Kỹ năng & Quy tắc bắt buộc** cho bất kỳ AI nào (Google Antigravity hoặc VS Code Codex / Copilot) khi làm việc trên kho mã nguồn dự án này.

---

## 1. NGUYÊN TẮC BẮT BUỘC TRƯỚC KHI CODE BẤT KỲ DÒNG NÀO

1. **Đọc `AGENT_CONTEXT.md` ở thư mục gốc**:
   - Đây là "bộ nhớ chung" duy nhất giữa 2 bên.
   - Xác định rõ: Đang ở Sprint mấy? Nhánh Git nào? Đã hoàn thành những gì? Đang gặp lỗi gì cần tránh?
2. **Kiểm tra môi trường ảo**:
   - Hệ điều hành: Windows.
   - Trình thông dịch Python: Bắt buộc dùng `.\.venv\Scripts\python.exe`.
   - Kiểm tra hệ thống: Chạy `.\.venv\Scripts\python.exe manage.py check` (phải đạt 0 lỗi).
3. **Tuân thủ tài liệu nguồn sự thật (Single Source of Truth)**:
   - Danh mục 31 Use Cases: `docs/Mô Tả Dự Án.md`.
   - Cấu trúc CSDL 32 bảng chuẩn: `docs/CSDL_He_thong_quan_ly_thuc_tap_Markdowfile.md`.
   - Quy tắc dự án: `GEMINI.md`.

---

## 2. KỶ LUẬT KIẾN TRÚC PHÂN TẦNG DJANGO MVT

Mọi ứng dụng Django (`dots`, `hoso`, `phancong`, `detai`, `thuchien`, `chamdiem`, `hethong`) phải tuân thủ nghiêm ngặt 5 tầng:

| Tầng | Tên file | Trách nhiệm bắt buộc | Điều cấm tuyệt đối |
| :--- | :--- | :--- | :--- |
| **Model** | `models.py` | Định nghĩa bảng, kiểu dữ liệu, khóa ngoại, constraints | ❌ CẤM tự ý đổi tên bảng, đổi tên cột, thêm cột ngoài CSDL 32 bảng |
| **Services** | `services.py` | Toàn bộ logic nghiệp vụ, thuật toán, validation, chuyển trạng thái | ❌ CẤM gọi `.update(trang_thai=...)` trực tiếp trong views |
| **State** | `core/state.py` | **Dịch vụ chuyển trạng thái duy nhất**: Mọi thay đổi `dot.trang_thai` và `ho_so.trang_thai` PHẢI qua đây | ❌ CẤM chuyển trạng thái đợt / hồ sơ bên ngoài `core/state.py` |
| **Selectors**| `selectors.py` | Chứa toàn bộ câu truy vấn (queries) có phân quyền theo User/Khoa/Vai trò | ❌ CẤM viết ORM queries phức tạp trong Views |
| **Views** | `views.py` | View mỏng: Nhận request, gọi selectors/services, redirect + messages | ❌ CẤM nhồi logic nghiệp vụ, tính toán điểm số trong views |
| **Templates**| `templates/` | Kế thừa `base.html`, tiếng Việt trang trọng, Tailwind CSS | ❌ CẤM hiển thị mã kỹ thuật/enum (`CHO_CHOT`, `PHAN_CONG`...) cho người dùng thật |

---

## 3. CÁC RÀNG BUỘC NGHIỆP VỤ BẤT DI BẤT DỊCH (SECURITY & INTEGRITY)

1. **Bảo mật điểm GPA đầu vào (`diem_dau_vao`)**:
   - **CHỈ DUY NHẤT Trưởng khoa** có quyền xem điểm đầu vào.
   - Tuyệt đối KHÔNG truyền biến này vào context của Giảng viên hoặc Sinh viên.
2. **Liêm chính điểm số**:
   - Sinh viên tuyệt đối **KHÔNG CÓ QUYỀN** nhập hoặc sửa bất kỳ điểm nào.
   - Giảng viên phản biện **KHÔNG ĐƯỢC TRÙNG** với GVHD của cùng một hồ sơ (`ho_so`).
   - Điểm đã gửi (`DA_GUI`) bị khóa chỉnh sửa.
3. **Cấu hình phân phối điểm (`dot_trong_so`)**:
   - Tổng tỷ trọng % các thành phần điểm của một đợt bắt buộc **= 100.0%**.
   - Mặc định Đồ án: GVHD 40% - Phản biện 20% - Hội đồng 40%.
   - Mặc định Thực tập: GVHD 40% - Nơi thực tập 30% - Phản biện 30%.
4. **Nhật ký hệ thống (`nhat_ky_he_thong`)**:
   - Chỉ ghi hành vi tác động của người dùng (Ai làm gì, lúc nào, đối tượng nào).
   - Tuyệt đối **KHÔNG ghi giá trị điểm số** vào mô tả log.
5. **Logo chuẩn**:
   - Luôn sử dụng ảnh `{% static 'images/logo_vinhuni.png' %}` trên mọi màn hình.

---

## 4. QUY TRÌNH BÀN GIAO (HANDOFF PROTOCOL GIỮA ANTIGRAVITY & CODEX)

Trước khi chuyển giao ca làm việc (Antigravity ↔ Codex):
1. **Kiểm thử tự động**:
   - Chạy: `.\.venv\Scripts\python.exe manage.py check` (0 lỗi).
   - Chạy: `.\.venv\Scripts\python.exe manage.py test` (100% tests PASS).
2. **Cập nhật `AGENT_CONTEXT.md`**:
   - Cập nhật mục `TRẠNG THÁI HIỆN TẠI`: Nhánh Git, số lượng tests PASS.
   - Tick vào checklist các use case / tính năng đã hoàn thành.
   - Ghi chú ngắn gọn vào mục `GHI CHÚ PHIÊN LÀM VIỆC CUỐI`: Đã làm gì, đã fix lỗi gì, bước tiếp theo là gì.
3. **Đồng bộ Git**:
   - `git add .`
   - `git commit -m "feat/fix: mô tả ngắn gọn"`
   - `git push origin <tên-nhánh>`
