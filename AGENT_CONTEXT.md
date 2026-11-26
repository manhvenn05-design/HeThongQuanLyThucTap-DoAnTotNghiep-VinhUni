# AGENT_CONTEXT.md — Bộ Nhớ Chung Cho AI
> **Mục đích**: File này là "não chung" giữa Antigravity và VS Code Codex.
> **Quy tắc bắt buộc**: AI nào làm việc PHẢI đọc file này trước, cập nhật trước khi kết thúc phiên.
> **Vị trí**: Project root (luôn commit lên Git cùng code)

---

## 🔴 TRẠNG THÁI HIỆN TẠI (Đọc đây trước tiên)

| Mục | Giá trị |
| :--- | :--- |
| **Sprint đang làm** | Sprint 4 — `THUC_HIEN` (UC16, UC17, UC18, UC31) |
| **Nhánh Git hiện tại** | `feature/sprint3-detai` (đã merge xong, chờ tạo sprint4) |
| **Lần cập nhật cuối** | 2026-11-26 09:45 — Antigravity |
| **Người cập nhật** | Antigravity |
| **Trạng thái server** | Chưa chạy (cần `python manage.py runserver`) |
| **Test suite** | 37/37 PASS (tất cả Sprint 1, 2, 3) |

---

## ✅ ĐÃ HOÀN THÀNH (Không cần làm lại)

### Sprint 1 — `CHUAN_BI` (UC03–UC06) ✅ 100%
- Nhánh: `feature/sprint1-backend` (đã push)
- Mô hình: `accounts`, `organization`, `dots`, `hoso`, `hethong`
- Views: Cổng đăng nhập, dashboard Trưởng khoa Sprint 1
- Tests: `hoso` 6/6, `organization` 7/7

### Sprint 2 — `PHAN_CONG` (UC07–UC11) ✅ 100%
- Nhánh: `feature/sprint2-phancong` (đã push)
- Thuật toán Snake Draft chia đều sinh viên theo GPA
- Views: Dashboard Sprint 2, màn hình xác nhận GVHD, Cổng Sinh viên Bước 1
- Tests: `phancong` 7/7

### Sprint 3 — `CHOT_DE_TAI` (UC12–UC15) ✅ 100%
- Nhánh: `feature/sprint3-detai` (đã push)
- Files tạo mới:
  - `detai/models.py` → Table 19 (`de_tai_goi_y`), Table 20 (`de_tai`)
  - `detai/services/topic_service.py` → UC12, UC13, UC14, UC15
  - `detai/selectors.py` → Các hàm truy vấn theo phân quyền
  - `detai/views.py` + `detai/urls.py` → 6 actions
  - `templates/sprint3/dashboard.html` → Dashboard Trưởng khoa
  - `templates/portals/lecturer_portal.html` → Hàng đợi duyệt đề tài, modal góp ý, modal thêm đề tài gợi ý
  - `templates/portals/student_portal.html` → Bước 2: Đăng ký / đề xuất đề tài
- Tests: `detai` 17/17

---

## 🚧 ĐANG LÀM — SPRINT 4 (`THUC_HIEN`)

**Use Cases**: UC16, UC17, UC18, UC31  
**Nhánh Git**: `feature/sprint4-thuchien` (chưa tạo)  
**Trạng thái**: Chưa bắt đầu

### Checklist Sprint 4
- [ ] Tạo nhánh `feature/sprint4-thuchien` từ `feature/sprint3-detai`
- [ ] Kiểm tra CSDL: Các bảng liên quan (xem mục CSDL bên dưới)
- [ ] Viết `thuchien/models.py` nếu cần bảng mới
- [ ] Chạy `makemigrations` & `migrate`
- [ ] Viết `thuchien/services.py` — logic UC16, UC17, UC18, UC31
- [ ] Viết `thuchien/selectors.py`
- [ ] Viết `thuchien/views.py` + `thuchien/urls.py`
- [ ] Cập nhật templates: Cổng GV (tab Tiến độ), Cổng SV (Bước 3), Dashboard TK Sprint 4
- [ ] Viết `thuchien/tests.py`
- [ ] Chạy full test suite: 0 lỗi, tất cả PASS
- [ ] Commit + Push `feature/sprint4-thuchien`

---

## 📐 KIẾN TRÚC DỰ ÁN

```
ProjectA/
├── accounts/       # Bảng nguoi_dung (đăng nhập, vai trò)
├── organization/   # khoa, bo_mon, giang_vien, sinh_vien
├── dots/           # dot (đợt thực tập/đồ án) — 6 trạng thái
├── hoso/           # ho_so — 7 trạng thái, diem_dau_vao (BÍ MẬT)
├── phancong/       # ban_phan_cong, phan_cong_huong_dan — Sprint 2
├── detai/          # de_tai_goi_y, de_tai — Sprint 3
├── hethong/        # thong_bao, nhat_ky_he_thong
├── core/
│   ├── constants.py    # Tất cả enum/constants (DotTrangThai, HoSoTrangThai...)
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

### Luồng Trạng Thái Hồ Sơ (`ho_so.trang_thai`)
```
CHO_PHAN_CONG → CHO_CHOT_DE_TAI → DANG_THUC_HIEN → CHO_CHAM_DIEM → DA_GUI_DIEM → HOAN_TAT
                                                  ↑
                              (do gvhd_phe_duyet_de_tai kích hoạt)
```

---

## 🔒 QUY TẮC BẤT DI BẤT DỊCH (AI PHẢI TUÂN THỦ)

1. **CSDL 32 bảng**: Không đổi tên bảng, không đổi tên cột. Tên `snake_case` tiếng Việt không dấu.
2. **Single State Transition**: Mọi thay đổi trạng thái `dot` và `ho_so` **BẮT BUỘC** gọi qua `core.state.chuyen_trang_thai_dot` / `chuyen_trang_thai_ho_so`. Tuyệt đối không gọi `.update(trang_thai=...)` trực tiếp trong views.
3. **Bảo mật `diem_dau_vao`**: Chỉ Trưởng khoa thấy GPA đầu vào. Không lộ ra bất kỳ template hoặc context nào khác.
4. **Sinh viên không nhập điểm**: Điểm chỉ do GVHD, GVPB, Hội đồng nhập.
5. **Nhật ký hệ thống**: Chỉ ghi hành vi, không ghi nội dung điểm số.
6. **Giảng viên phản biện ≠ GVHD** của cùng một hồ sơ.
7. **UI tiếng Việt trang trọng**: Không để lộ tên enum/mã kỹ thuật (`CHO_CHOT`, `PHAN_CONG`...) ra giao diện người dùng thực.
8. **Logo**: Dùng `{% static 'images/logo_vinhuni.png' %}` cho mọi màn hình.

---

## 📋 CSDL CÁC BẢNG SPRINT 4 CẦN BIẾT

Theo `docs/CSDL_He_thong_quan_ly_thuc_tap_Markdowfile.md`:

### Bảng liên quan UC16, UC17, UC18, UC31 (cần kiểm tra chính xác trong docs):
- **`tuan_theo_doi`** (nếu có): Theo dõi tiến độ hàng tuần
- **`minh_chung`** (nếu có): File/link minh chứng sinh viên nộp
- **`yeu_cau_minh_chung`** (nếu có): Danh mục yêu cầu GVHD ban hành

> ⚠️ **Lưu ý**: Trước khi code Sprint 4, AI phải đọc lại chính xác tên bảng và tên cột từ `docs/CSDL_He_thong_quan_ly_thuc_tap_Markdowfile.md` để tránh sai lệch.

---

## 🔄 HANDOFF PROTOCOL (Bắt buộc trước khi kết thúc phiên)

### Khi kết thúc phiên Antigravity → chuyển sang VS Code Codex:
```
1. git add . && git commit -m "session: [mô tả ngắn gọn những gì đã làm]"
2. git push origin [tên-nhánh-hiện-tại]
3. Cập nhật AGENT_CONTEXT.md:
   - Cập nhật "TRẠNG THÁI HIỆN TẠI"
   - Tick vào checklist những việc đã hoàn thành
   - Ghi vào "GHI CHÚ PHIÊN LÀM VIỆC CUỐI" bên dưới
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

**Phiên**: 2026-11-26 09:45 | **Nền tảng**: Antigravity  
**Đã làm**:
- Hoàn tất Sprint 3 (UC12-UC15): 17 unit tests mới, fix lỗi field `loai` vs `loai_su_kien` trên model `thong_bao`
- Cập nhật modal feedback GVHD (`#gvFeedbackModal`): thêm `form id`, `action` động qua JS, `name="gop_y"` trên textarea
- Thêm modal `#addSuggestedTopicModal`: POST thực sự đến `detai:tao_de_tai_goi_y`
- Push nhánh `feature/sprint3-detai` lên GitHub

**Chưa làm / Bước tiếp theo**:
- Tạo nhánh `feature/sprint4-thuchien`
- Đọc CSDL Sprint 4 từ docs
- Bắt đầu UC16: GVHD ban hành danh mục minh chứng

**Lỗi đã gặp & cách fix**:
- `thong_bao() got unexpected keyword arguments: 'loai_su_kien'`: Model dùng field `loai`, không phải `loai_su_kien`. Đã fix trong `topic_service.py`.
- Git `index.lock Permission denied` trên Windows: Chạy `git add` với `BypassSandbox: true`.
