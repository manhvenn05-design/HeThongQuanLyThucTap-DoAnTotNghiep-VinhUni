# AGENT_CONTEXT.md — Bộ Nhớ Chung Cho AI
> **Mục đích**: File này là "não chung" giữa Antigravity và VS Code Codex.
> **Quy tắc bắt buộc**: AI nào làm việc PHẢI đọc file này trước, cập nhật trước khi kết thúc phiên.
> **Vị trí**: Project root (luôn commit lên Git cùng code)

---

## 🔴 TRẠNG THÁI HIỆN TẠI (Đọc đây trước tiên)

| Mục | Giá trị |
| :--- | :--- |
| **Giai đoạn hiện tại** | Đã hoàn thành cấu hình phân phối điểm (UC03 bổ sung) → Chuẩn bị Sprint 4 (`THUC_HIEN`) |
| **Nhánh Git hiện tại** | `feature/sprint3-detai` |
| **Lần cập nhật cuối** | 2026-11-28 12:55 — Antigravity |
| **Người cập nhật** | Antigravity |
| **Trạng thái server** | Sẵn sàng chạy (`python manage.py runserver`) |
| **Test suite** | **47/47 PASS (100%)** — `dots` 10/10, `detai` 17/17, `phancong` 7/7, `hoso` 6/6, `organization` 7/7 |

---

## ✅ ĐÃ HOÀN THÀNH (Không cần làm lại)

### 1. Bổ sung: Cấu hình phân phối điểm thành phần (UC03) ✅ 100%
- **Yêu cầu từ Thầy hướng dẫn**: Cho phép Trưởng khoa cấu hình linh hoạt phân phối điểm thành phần (% trọng số) cho từng đợt, tổng bắt buộc bằng 100%.
- **Bảng CSDL**: Table 11 (`dot_trong_so` trong `dots/models.py`)
- **Tỷ lệ chuẩn hóa mặc định**:
  - **Đồ án (`DO_AN`)**: GVHD Hướng dẫn **40%** + Phản biện **20%** + Hội đồng **40%** = 100%.
  - **Thực tập (`THUC_TAP`)**: GVHD Hướng dẫn **40%** + Đơn vị thực tập **30%** + Phản biện **30%** = 100%.
- **Files triển khai**:
  - `dots/services.py`: `TrongSoValidationError`, `lay_trong_so_mac_dinh`, `khoi_tao_trong_so_mac_dinh`, `cap_nhat_trong_so_dot` (validate tổng = 100%, không âm, ghi `nhat_ky_he_thong`).
  - `dots/selectors.py`: `get_dot_weights` (tự động khởi tạo mặc định nếu đợt chưa có).
  - `dots/views.py`: `update_dot_weights_view` (POST `/dot/<id>/update-weights/`).
  - `config/urls.py`: path `update_dot_weights`.
  - `templates/sprint1/dashboard.html`: Khối hiển thị thẻ trọng số điểm + Modal `#updateWeightsModal` tính tổng realtime bằng Javascript, cảnh báo lỗi và chặn submit nếu tổng != 100%.
  - `dots/tests.py`: **10/10 unit tests PASS** (Validation tổng, số âm, đợt hoàn tất, selector, HTTP POST).

### 2. Sprint 1 — `CHUAN_BI` (UC03–UC06) ✅ 100%
- Nhánh: `feature/sprint1-backend`
- Mô hình: `accounts`, `organization`, `dots`, `hoso`, `hethong`
- Tiếp nhận Excel danh sách, đồng bộ điểm GPA USMART
- Tests: `hoso` 6/6, `organization` 7/7, `dots` 10/10

### 3. Sprint 2 — `PHAN_CONG` (UC07–UC11) ✅ 100%
- Nhánh: `feature/sprint2-phancong`
- Thuật toán Snake Draft ziczac chia đều sinh viên theo GPA
- Views: Dashboard Sprint 2, GVHD xác nhận phân công, Cổng Sinh viên Bước 1
- Tests: `phancong` 7/7

### 4. Sprint 3 — `CHOT_DE_TAI` (UC12–UC15) ✅ 100%
- Nhánh: `feature/sprint3-detai`
- Table 19 (`de_tai_goi_y`), Table 20 (`de_tai`)
- GVHD đưa đề tài gợi ý, SV chọn hoặc đề xuất, GVHD phê duyệt (Chốt / Góp ý trả lại / Duyệt tất cả)
- Tests: `detai` 17/17

---

## 🚧 BƯỚC TIẾP THEO — SPRINT 4 (`THUC_HIEN`)

**Use Cases**: UC16, UC17, UC18, UC31  
**Nhánh Git**: `feature/sprint4-thuchien` (tạo từ `feature/sprint3-detai`)  
**Mục tiêu Sprint 4**:
1. **UC16**: GVHD ban hành danh mục yêu cầu minh chứng / sản phẩm nộp theo tuần (Bắt buộc / Khuyến khích).
2. **UC17**: Sinh viên nộp minh chứng định kỳ hàng tuần (File, Git URL, ERD, Video demo).
3. **UC18**: GVHD theo dõi, đánh giá tiến độ sinh viên từng tuần (Đạt / Cần bổ sung / Chậm tiến độ).
4. **UC31**: Trưởng khoa giám sát toàn cảnh tiến độ các nhóm, phát hiện và cảnh báo sinh viên chậm nộp.

### Checklist Sprint 4
- [ ] Tạo nhánh `git checkout -b feature/sprint4-thuchien`
- [ ] Kiểm tra bảng CSDL: `minh_chung` (Bảng 24), `tuan_theo_doi` hoặc tương đương theo `docs/CSDL_He_thong_quan_ly_thuc_tap_Markdowfile.md`
- [ ] Viết models/migrations nếu cần
- [ ] Viết `thuchien/services.py`, `thuchien/selectors.py`, `thuchien/views.py`
- [ ] Cập nhật giao diện: Cổng GV (Tab Tiến độ), Cổng SV (Bước 3: Nộp tiến độ), Dashboard Sprint 4
- [ ] Viết `thuchien/tests.py` và chạy full test suite (phải 0 lỗi)

---

## 📐 KIẾN TRÚC DỰ ÁN

```
ProjectA/
├── accounts/       # Bảng nguoi_dung (đăng nhập, vai trò)
├── organization/   # khoa, bo_mon, giang_vien, sinh_vien
├── dots/           # dot, dot_moc_thoi_gian, dot_trong_so (Cấu hình điểm UC03)
├── hoso/           # ho_so, diem_dau_vao (BÍ MẬT chỉ Trưởng khoa xem)
├── phancong/       # ban_phan_cong, phan_cong_huong_dan (Sprint 2)
├── detai/          # de_tai_goi_y, de_tai (Sprint 3)
├── hethong/        # thong_bao, nhat_ky_he_thong
├── core/
│   ├── constants.py    # Tất cả enum/constants (DotTrangThai, HoSoTrangThai, ThanhPhanDiem...)
│   └── state.py        # Dịch vụ chuyển trạng thái duy nhất (BẮT BUỘC dùng)
└── templates/
    ├── base.html
    ├── portals/        # student_portal.html, lecturer_portal.html
    ├── sprint1/ → sprint6/   # Dashboard Trưởng khoa theo sprint
    └── components/     # navbar, sidebar, modal...
```

### Luồng Trạng Thái Đợt (`dot.trang_thai`)
```
CHUAN_BI → PHAN_CONG → CHOT_DE_TAI → THUC_HIEN → CHAM_DIEM → HOAN_TAT
  (S1)        (S2)         (S3)          (S4)         (S5)        (S6)
```

---

## 🔒 QUY TẮC BẤT DI BẤT DỊCH (AI PHẢI TUÂN THỦ)

1. **CSDL 32 bảng**: Không đổi tên bảng, không đổi tên cột. Tên `snake_case` tiếng Việt không dấu.
2. **Single State Transition**: Mọi thay đổi trạng thái `dot` và `ho_so` **BẮT BUỘC** gọi qua `core.state.chuyen_trang_thai_dot` / `chuyen_trang_thai_ho_so`.
3. **Bảo mật `diem_dau_vao`**: Chỉ Trưởng khoa thấy GPA đầu vào.
4. **Sinh viên không nhập điểm**: Điểm chỉ do GVHD, GVPB, Hội đồng nhập.
5. **Cấu hình trọng số điểm**: Tổng trọng số các thành phần bắt buộc = 100%.
6. **Nhật ký hệ thống**: Chỉ ghi hành vi tác động, không ghi giá trị điểm số.
7. **Giảng viên phản biện ≠ GVHD** của cùng một hồ sơ.
8. **UI tiếng Việt trang trọng**: Không để lộ tên enum/mã kỹ thuật (`CHO_CHOT`, `PHAN_CONG`...) ra giao diện người dùng thực.
9. **Logo**: Dùng `{% static 'images/logo_vinhuni.png' %}` cho mọi màn hình.

---

## 🔄 HANDOFF PROTOCOL (Bắt buộc trước khi kết thúc phiên)

### Khi kết thúc phiên Antigravity → chuyển sang VS Code Codex:
```
1. git add . && git commit -m "session: [mô tả ngắn gọn những gì đã làm]"
2. git push origin [tên-nhánh-hiện-tại]
3. Cập nhật AGENT_CONTEXT.md
4. git add AGENT_CONTEXT.md && git commit -m "context: update handoff notes"
5. git push
```

### Khi bắt đầu phiên mới (dù là AI nào):
```
1. git pull origin [tên-nhánh]
2. Đọc AGENT_CONTEXT.md từ đầu đến cuối
3. Kiểm tra: python manage.py check (phải 0 lỗi)
4. Bắt đầu làm việc từ checklist còn lại
```

---

## 📝 GHI CHÚ PHIÊN LÀM VIỆC CUỐI

**Phiên**: 2026-11-28 12:55 | **Nền tảng**: Antigravity  
**Đã làm**:
- Triển khai trọn vẹn yêu cầu cấu hình phân phối điểm linh hoạt theo góp ý của Thầy (UC03):
  * Cập nhật `PRESETS_CONFIG` với cơ cấu chuẩn: Đồ án (40% HD - 20% PB - 40% HĐ), Thực tập (40% HD - 30% NTT - 30% PB).
  * Viết service nghiệp vụ `cap_nhat_trong_so_dot`, `khoi_tao_trong_so_mac_dinh`, `lay_trong_so_mac_dinh` và exception `TrongSoValidationError` tại `dots/services.py`.
  * Thêm selector `get_dot_weights` tự động khởi tạo trọng số nếu chưa có.
  * Thêm view `update_dot_weights_view` và route URL `update_dot_weights`.
  * Tích hợp giao diện: Thẻ hiển thị tỷ lệ % + Modal tùy chỉnh `#updateWeightsModal` với thanh báo động realtime tính tổng trọng số.
  * Viết 10 unit tests mới trong `dots/tests.py` đạt 100% PASS.
  * Chạy toàn bộ test suite dự án: **47/47 tests PASS (0 errors)**.

**Chưa làm / Bước tiếp theo**:
- Tạo nhánh `feature/sprint4-thuchien` từ `feature/sprint3-detai`.
- Bắt đầu triển khai Sprint 4 (UC16, UC17, UC18, UC31).
