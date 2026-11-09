# PROJECT_SPEC.md – Hệ thống quản lý điều phối thực tập và đồ án tốt nghiệp

> Trường Kỹ thuật và Công nghệ, Đại học Vinh. Phiên bản tài liệu 1.0 (bản nháp chờ thầy xác nhận một số điểm, xem mục 19).
> Tài liệu này là **nguồn sự thật duy nhất** để AI agent xây dựng hệ thống. Đọc hết trước khi viết code.

---

## 0. Hướng dẫn cho AI agent (đọc đầu tiên)

1. **Thứ tự ưu tiên khi có mâu thuẫn:** (1) mục 5 vòng đời và mục 7 quy tắc nghiệp vụ; (2) mục 10 CSDL; (3) mục 6 use case; (4) mục 13 màn hình; (5) các tài liệu khác của người dùng (sơ đồ, sprint giao diện). Nếu sprint giao diện của người dùng mâu thuẫn với tài liệu này, **dừng lại và hỏi**, không tự chọn.
2. **Không tự thêm tính năng** ngoài 31 use case ở mục 6. Mục 2 liệt kê những gì nằm ngoài phạm vi.
3. **Không đổi tên** bảng, cột, giá trị liệt kê (enum), mã trạng thái. Tên bảng và cột viết tiếng Việt không dấu, dạng `snake_case`, giữ đúng như mục 10 và 11.
4. Khi gặp điểm chưa rõ, dùng giá trị mặc định ghi ở mục 19 và đánh dấu trong code bằng comment `# ASSUMPTION: ...`. Không im lặng chọn một cách khác.
5. **Quy tắc bất di bất dịch (không bao giờ vi phạm):**
   - Không lưu mật khẩu của cổng sinh viên USMART ở bất kỳ đâu (CSDL, log, session).
   - Sinh viên không bao giờ nhập hay sửa điểm.
   - Mỗi khoa chỉ thấy dữ liệu khoa mình; giảng viên chỉ thấy hồ sơ mình phụ trách; sinh viên chỉ thấy hồ sơ của mình. Kiểm tra quyền ở **mọi view**, không chỉ ẩn nút.
   - Điểm trung bình đầu vào chỉ trưởng khoa xem được.
   - Nhật ký hệ thống không ghi giá trị điểm.
   - Điểm đã gửi (`DA_GUI`) và hồ sơ đã chốt không sửa được.
   - Phản biện không được là giảng viên hướng dẫn của cùng hồ sơ.
6. Mọi thay đổi trạng thái hồ sơ/đợt đi qua **một hàm dịch vụ duy nhất** (mục 5.3), không `update()` trạng thái rải rác trong view.
7. Mọi giao diện bằng **tiếng Việt**; ngôn ngữ làm việc quen thuộc, ít bước (người dùng chính là trưởng khoa và giảng viên không rành công nghệ).
8. Viết test cho các phần ở mục 17.3. Sau mỗi giai đoạn chạy test và chạy thử bằng dữ liệu mẫu (mục 18).

---

## 1. Tổng quan bài toán

**Hệ thống** hỗ trợ một khoa điều phối trọn vẹn một **đợt thực tập hoặc đồ án tốt nghiệp**: nhận danh sách sinh viên, phân công giảng viên hướng dẫn (GVHD) công bằng, chốt đề tài, theo dõi tiến độ qua minh chứng, chấm điểm nhiều thành phần, tính điểm cuối theo trọng số và lưu hồ sơ.

**Luồng thực tế (do thầy mô tả, là luồng chính):**

1. Phòng đào tạo có danh sách sinh viên đăng ký học phần (tên, mã sinh viên, số lượng) và **gửi file Excel** cho trưởng khoa.
2. Trưởng khoa tải file lên hệ thống, hệ thống tự bóc tách, lấy điểm trung bình tích lũy từ USMART.
3. Trưởng khoa phân sinh viên cho GVHD (có gợi ý chia đều giỏi/yếu), gửi **bản nháp phân công**.
4. GVHD xác nhận hoặc từ chối. Khi mọi GVHD đồng ý, trưởng khoa **công bố chính thức** cho giảng viên và sinh viên.
5. Sinh viên chọn đề tài GVHD đưa ra hoặc tự đề xuất; GVHD chốt hoặc trả lại.
6. Giai đoạn thực hiện: sinh viên nộp **minh chứng tiến độ** theo mốc; GVHD nhận xét; trưởng khoa theo dõi.
7. Sinh viên nộp báo cáo/khóa luận cuối. GVHD chấm điểm hướng dẫn và nhập điểm nơi thực tập (đối chiếu bản gốc có dấu, có thể xác minh với nơi thực tập).
8. Trưởng khoa phân công **phản biện** (hoặc **hội đồng** với đồ án); người chấm nhập điểm.
9. Hệ thống tính **điểm cuối theo trọng số** của đợt; trưởng khoa tổng hợp, **chốt và lưu hồ sơ**; sinh viên xem kết quả.

**Mục tiêu thiết kế:** ít bước, hướng theo "việc đang chờ tôi", minh bạch trạng thái, làm hàng loạt, giảm nhập tay, chống gian lận điểm nơi thực tập, hệ thống dùng được cho nhiều khoa/trường (cấu hình theo đợt, không cứng hóa quy trình).

---

## 2. Phạm vi

**Trong phạm vi:** 31 use case ở mục 6, 7 tác nhân ở mục 4, thông báo trong ứng dụng, nhật ký hệ thống.

**Ngoài phạm vi (không làm, không thêm):**
- Gửi email/SMS (chỉ thông báo trong ứng dụng). ASSUMPTION.
- Tài khoản cho Phòng đào tạo, giáo vụ khoa, thư ký hội đồng, doanh nghiệp/nơi thực tập (đều là bên ngoài hệ thống hoặc để sau).
- Lấy điểm rèn luyện, điểm từng môn (chỉ lấy điểm trung bình tích lũy hệ 4 và số tín chỉ tích lũy).
- Chấm điểm theo rubric/tiêu chí chi tiết.
- Ứng dụng di động riêng (giao diện web đáp ứng điện thoại cho sinh viên là đủ).
- Chữ ký số, xuất bảng điểm chính thức có dấu.

---

## 3. Công nghệ và kiến trúc

| Hạng mục | Quyết định |
|---|---|
| Kiến trúc | Monolithic phân tầng, mô hình MVT của Django |
| Ngôn ngữ, framework | Python 3.12+, Django 5.x |
| Giao diện | Django Template + Bootstrap 5 + HTMX (không SPA, không React) |
| CSDL | PostgreSQL 16 |
| Triển khai | Docker Compose (web, db, nginx); cấu hình bằng biến môi trường |
| Phân quyền | RBAC + kiểm tra phạm vi theo khoa/hồ sơ ở mọi view |
| Tệp tải lên | Lưu ra đĩa (volume), CSDL chỉ giữ đường dẫn; phục vụ qua view có kiểm tra quyền |
| Đọc Excel | `openpyxl` |
| Kiểm thử | `pytest` + `pytest-django` |
| Múi giờ, ngôn ngữ | `Asia/Ho_Chi_Minh`, `vi` |

**Phân tầng trong mỗi app Django:**
- `models.py`: chỉ dữ liệu và ràng buộc.
- `services.py`: **toàn bộ nghiệp vụ** (đổi trạng thái, tính điểm, gợi ý chia đều, kiểm tra quy tắc). View mỏng, chỉ gọi service.
- `selectors.py`: truy vấn có phạm vi quyền (`for_user`).
- `views.py`, `urls.py`, `forms.py`, `templates/`: giao diện, HTMX trả về mảnh HTML (partial).
- `tests/`.

**Tích hợp ngoài:** cổng sinh viên USMART qua lớp **adapter** (mục 9), có bộ giả lập cho phát triển.

---

## 4. Tác nhân và phân quyền

### 4.1 Tác nhân

| Mã | Tác nhân | Là ai | Ghi chú triển khai |
|---|---|---|---|
| SV | Sinh viên | Sinh viên trong danh sách đợt | Xác định qua bản ghi `sinh_vien` |
| TKhoa | Trưởng khoa | Trưởng một khoa; **tạm thời** cũng mở đợt và tải danh sách | Vai trò `TRUONG_KHOA`, giới hạn theo `khoa_id` |
| HD | Giảng viên hướng dẫn | Giảng viên được phân hướng dẫn hồ sơ | Là **vai của giảng viên theo từng hồ sơ**, không phải loại tài khoản |
| PB | Giảng viên phản biện | Được phân phản biện, **khác** HD của hồ sơ đó | Theo `phan_cong_cham` |
| HĐ | Thành viên hội đồng | Giảng viên trong hội đồng (đồ án) | Theo `thanh_vien_hoi_dong` |
| QT | Quản trị hệ thống | Cán bộ kỹ thuật | Vai trò `QUAN_TRI`; không xem nội dung chấm điểm |
| USMART | Cổng sinh viên (tác nhân phụ) | Hệ thống ngoài | Cung cấp xác thực và điểm TB |

Bên ngoài hệ thống (không có tài khoản): **Phòng đào tạo** (gửi file Excel), **nơi thực tập** (giấy xác nhận, xác minh qua điện thoại/email do HD thực hiện).

HD, PB, HĐ là **ba vai của cùng một giảng viên**: một tài khoản giảng viên có thể giữ cả ba cùng lúc ở các hồ sơ khác nhau. Màn đầu của giảng viên gom việc theo vai.

### 4.2 Ma trận quyền (tóm tắt)

| Tài nguyên / hành động | SV | HD | PB | HĐ | TKhoa | QT |
|---|---|---|---|---|---|---|
| Đăng nhập, xem thông báo của mình | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| Mở đợt, cấu hình, tải/xác nhận danh sách (khoa mình) | | | | | ✔ | |
| Lấy điểm TB, xem điểm TB đầu vào | | | | | ✔ | |
| Soạn, gửi, công bố phân công; đổi HD sau công bố | | | | | ✔ | |
| Xác nhận/từ chối phân công (của mình) | | ✔ | | | | |
| Xem GVHD của mình (sau công bố) | ✔ | | | | | |
| Đưa ra đề tài, chốt/trả lại đề tài (hồ sơ mình HD) | | ✔ | | | | |
| Chọn/đề xuất đề tài (hồ sơ của mình) | ✔ | | | | | |
| Nộp minh chứng, báo cáo cuối, thông tin nơi thực tập | ✔ | | | | | |
| Nhận xét minh chứng | | ✔ | | | | |
| Theo dõi tiến độ cả khoa, nhắc hàng loạt | | | | | ✔ | |
| Chấm hướng dẫn, nhập điểm nơi thực tập, xác minh | | ✔ | | | | |
| Phân công phản biện/hội đồng | | | | | ✔ | |
| Chấm phản biện (hồ sơ được phân) | | | ✔ | | | |
| Chấm hội đồng (buổi/hồ sơ của hội đồng mình) | | | | ✔ | | |
| Tổng hợp, chốt, lưu hồ sơ (khoa mình) | | | | | ✔ | |
| Xem kết quả của mình (khi Hoàn tất) | ✔ | | | | | |
| Quản lý tài khoản, phân quyền, danh mục khoa/bộ môn | | | | | | ✔ |
| Xem nhật ký hệ thống | | | | | | ✔ |
| Xem nội dung điểm đang chấm của người khác | ✘ | ✘ | ✘ | ✘ | ✔ (điểm đã gửi) | ✘ |

**Quy tắc phạm vi (bắt buộc cài ở lớp selector):**
- TKhoa: `dot.khoa_id` ∈ các khoa được gán trong `nguoi_dung_vai_tro`.
- HD: `ho_so.giang_vien_huong_dan_id = giảng viên đó` (hoặc dòng `phan_cong_huong_dan` đang chờ xác nhận gửi cho họ).
- PB/HĐ: chỉ hồ sơ có `phan_cong_cham` tương ứng; PB không xem điểm HD/nơi thực tập của hồ sơ trước khi mình gửi điểm (ASSUMPTION, để độc lập).
- SV: `ho_so.sinh_vien_id` là mình; chỉ thấy GVHD sau khi bản phân công `DA_CONG_BO`; chỉ thấy điểm khi hồ sơ `HOAN_TAT`.
- Một giảng viên giữ nhiều vai: gộp quyền theo từng hồ sơ, không theo tài khoản.

---

## 5. Vòng đời

### 5.1 Đợt (6 giai đoạn, `dot.trang_thai`)

`CHUAN_BI` → `PHAN_CONG` → `CHOT_DE_TAI` → `THUC_HIEN` → `CHAM_DIEM` → `HOAN_TAT`

| Giai đoạn | Chức năng mở | Chuyển sang giai đoạn sau khi |
|---|---|---|
| CHUAN_BI | Cấu hình đợt, tải danh sách, xem trước, xác nhận, lấy điểm | TKhoa bấm "Sang phân công" (cần danh sách đã xác nhận) |
| PHAN_CONG | Soạn nháp, gợi ý chia đều, gửi, xác nhận, công bố | Công bố danh sách chính thức (UC09) – tự động |
| CHOT_DE_TAI | Đưa ra/chọn/đề xuất/chốt đề tài | TKhoa bấm chuyển (ASSUMPTION: thủ công) |
| THUC_HIEN | Nộp minh chứng, nhận xét, theo dõi | TKhoa bấm chuyển (ASSUMPTION: thủ công) |
| CHAM_DIEM | Nộp báo cáo cuối, chấm, phân công phản biện/hội đồng | TKhoa bấm chuyển (ASSUMPTION) |
| HOAN_TAT | Tổng hợp, chốt, lưu hồ sơ; chỉ xem | Tự động khi mọi hồ sơ `HOAN_TAT` |

Chức năng của giai đoạn chưa tới **vẫn hiện nhưng khóa**, kèm lý do ngắn ("Mở khi trưởng khoa công bố danh sách"). Việc gate thật dựa trên **trạng thái hồ sơ** (5.2); giai đoạn đợt chủ yếu để hiển thị và chặn sớm.

### 5.2 Hồ sơ (7 trạng thái, `ho_so.trang_thai`)

```
TRONG_DANH_SACH ──(TKhoa gửi bản phân công, UC07)──► CHO_XAC_NHAN
CHO_XAC_NHAN ──(HD từ chối, UC10)──► TRONG_DANH_SACH      [nhánh quay lại duy nhất]
CHO_XAC_NHAN ──(TKhoa công bố khi mọi HD đã đồng ý, UC09)──► CHO_CHOT_DE_TAI
CHO_CHOT_DE_TAI ──(HD chốt đề tài, UC15)──► DANG_THUC_HIEN        [trả lại đề tài: ở nguyên trạng thái]
DANG_THUC_HIEN ──(SV nộp báo cáo cuối, UC19)──► CHAM_HUONG_DAN
CHAM_HUONG_DAN ──(HD gửi điểm, UC20/UC21)──► CHO_PHAN_BIEN
CHO_PHAN_BIEN ──(TKhoa chốt khi đủ điểm, UC25)──► HOAN_TAT
```

Bảng chuyển trạng thái (cài thành bảng tra trong `services`):

| Từ | Sự kiện | Đến | Ai | Điều kiện (guard) |
|---|---|---|---|---|
| (chưa có) | `XAC_NHAN_DANH_SACH` | TRONG_DANH_SACH | TKhoa | Lần nhập không còn dòng lỗi |
| TRONG_DANH_SACH | `GUI_PHAN_CONG` | CHO_XAC_NHAN | TKhoa | Có dòng phân công; không vượt hạn mức |
| CHO_XAC_NHAN | `GV_TU_CHOI` | TRONG_DANH_SACH | HD | Bắt buộc có lý do |
| CHO_XAC_NHAN | `CONG_BO` | CHO_CHOT_DE_TAI | TKhoa | Mọi dòng phân công hiệu lực `DONG_Y`, không còn hồ sơ chưa giao |
| CHO_CHOT_DE_TAI | `CHOT_DE_TAI` | DANG_THUC_HIEN | HD | `de_tai` đang `CHO_CHOT` của hồ sơ |
| DANG_THUC_HIEN | `NOP_BAO_CAO_CUOI` | CHAM_HUONG_DAN | SV | Mốc nộp báo cáo cuối đang mở; có tệp |
| CHAM_HUONG_DAN | `GUI_DIEM_HD` | CHO_PHAN_BIEN | HD | Đủ điểm thành phần của HD; (thực tập) đã đối chiếu bản gốc |
| CHO_PHAN_BIEN | `CHOT_HO_SO` | HOAN_TAT | TKhoa | Đủ mọi thành phần có trọng số > 0 ở trạng thái `DA_GUI` |

Ghi chú: nếu đợt không có thành phần phản biện/hội đồng (trọng số 0), trạng thái `CHO_PHAN_BIEN` hiển thị là "Chờ tổng hợp" và bỏ qua UC22 (ASSUMPTION). Sau `CONG_BO`, trưởng khoa có thể **đổi HD** (ASSUMPTION, mục 6 UC09): dòng phân công cũ → `DA_THAY_THE` kèm lý do, tạo dòng mới `DONG_Y` sau khi HD mới xác nhận; hồ sơ giữ nguyên trạng thái.

### 5.3 Hàm chuyển trạng thái duy nhất

```python
# core/state.py  (ví dụ chữ ký, agent cài đặt đầy đủ)
def transition_ho_so(ho_so, event, actor, **ctx) -> HoSo:
    """Kiểm tra bảng chuyển + guard + quyền actor, đổi trạng thái trong transaction,
    ghi nhat_ky_he_thong (không ghi giá trị điểm), phát thong_bao. Ném DomainError nếu sai."""
```

---

## 6. Use case chi tiết (31)

Mỗi use case: tác nhân, điều kiện trước, kết quả, bảng dữ liệu chính. «include»/«extend» theo sơ đồ use case.

| UC | Tên | Tác nhân | Điều kiện trước | Kết quả chính | Bảng chính |
|---|---|---|---|---|---|
| UC01 | Đăng nhập bằng tài khoản cổng | Tất cả; USMART | Người dùng có trong `nguoi_dung` (từ danh sách hoặc quản trị) | Tạo phiên; chuyển vào màn đầu theo vai trò. Lần đầu: lưu `tai_khoan_lien_ket`. Không có tài khoản/đợt: màn "Bạn chưa thuộc đợt này" | nguoi_dung, tai_khoan_lien_ket, nhat_ky_he_thong |
| UC02 | Xem thông báo | Tất cả | Đã đăng nhập | Chuông cố định mọi màn; bấm thông báo → màn xử lý; đánh dấu đã đọc | thong_bao |
| UC03 | Mở đợt và cấu hình đợt | TKhoa | Có quyền khoa | Tạo `dot` (CHUAN_BI) + mốc + trọng số; tổng trọng số = 100; `hinh_thuc_cham = HOI_DONG` chỉ khi `loai = DO_AN` | dot, dot_moc_thoi_gian, dot_trong_so |
| UC04 | Tải file danh sách lên | TKhoa | Đợt CHUAN_BI. «include» UC05 | Bóc tách file Excel (mã SV, họ tên, lớp, [điểm]); tạo `lan_nhap_danh_sach` XEM_TRUOC | lan_nhap_danh_sach, dong_nhap_danh_sach |
| UC05 | Xem trước và xác nhận danh sách | TKhoa | Có lần nhập XEM_TRUOC | Sửa/bỏ dòng lỗi; xác nhận → tạo/ cập nhật `nguoi_dung` (CHUA_KICH_HOAT), `sinh_vien`, `ho_so` TRONG_DANH_SACH | ho_so, sinh_vien, nguoi_dung |
| UC06 | Lấy điểm TB tích lũy từ USMART | TKhoa; USMART | Danh sách đã xác nhận | Lưu `diem_dau_vao` (hệ 4 + tín chỉ), một lần, ghi ngày; thiếu → nguồn KHONG_CO; báo "N sinh viên, M có điểm, K chưa có" | diem_dau_vao, lan_lay_diem |
| UC07 | Soạn bản nháp phân công (và gửi) | TKhoa | Đợt PHAN_CONG | Hai khung sinh viên/giảng viên, kéo thả, kiểm tra hạn mức, tự lưu nháp; "Gửi giảng viên xác nhận" → ho_so CHO_XAC_NHAN, thông báo HD | ban_phan_cong, phan_cong_huong_dan |
| UC08 | Gợi ý chia đều theo điểm | TKhoa | «extend» UC07 | Sinh các dòng phân công nháp `la_goi_y = TRUE` theo thuật toán mục 8.1; TKhoa chỉnh tay | phan_cong_huong_dan |
| UC09 | Công bố danh sách chính thức | TKhoa | Mọi dòng hiệu lực DONG_Y | Ban `DA_CONG_BO`; gán `ho_so.giang_vien_huong_dan_id`; ho_so CHO_CHOT_DE_TAI; đợt → CHOT_DE_TAI; thông báo HD và SV. Hộp xác nhận nêu hậu quả. (Mở rộng ASSUMPTION: đổi HD sau công bố với lý do bắt buộc, dòng cũ `DA_THAY_THE`) | ban_phan_cong, ho_so, phan_cong_huong_dan |
| UC10 | Xác nhận hoặc từ chối phân công | HD | Có dòng CHO_XAC_NHAN gửi cho mình | "Đồng ý tất cả" hoặc "Từ chối" (lý do bắt buộc); không hiện điểm SV; kiểm tra hạn mức; thông báo TKhoa | phan_cong_huong_dan, ho_so |
| UC11 | Xem giảng viên hướng dẫn | SV | Ban `DA_CONG_BO` | Hiển thị GVHD; trước đó "Chưa có giảng viên hướng dẫn" | ho_so |
| UC12 | Đưa ra đề tài | HD | Đợt CHOT_DE_TAI; tùy chọn | Tạo `de_tai_goi_y` (MO/DONG, số lượng tối đa) | de_tai_goi_y |
| UC13 | Chọn đề tài giảng viên đưa ra | SV | Hồ sơ CHO_CHOT_DE_TAI, chưa có đề tài CHO_CHOT/DA_CHOT | `de_tai` nguồn GV_DUA_RA, CHO_CHOT; kiểm tra còn chỗ; thông báo HD | de_tai |
| UC14 | Đề xuất đề tài mới | SV | Như UC13 | `de_tai` nguồn SV_DE_XUAT, CHO_CHOT | de_tai |
| UC15 | Chốt hoặc trả lại đề tài | HD | Có đề tài CHO_CHOT | Chấp nhận → DA_CHOT, `ho_so.de_tai_hien_tai_id`, ho_so DANG_THUC_HIEN; trả lại → TRA_LAI + góp ý bắt buộc; có chấp nhận hàng loạt | de_tai, ho_so |
| UC16 | Nộp minh chứng tiến độ | SV | Hồ sơ DANG_THUC_HIEN; mốc đang mở | Tạo `minh_chung` + `tep_dinh_kem`; quá hạn vẫn nhận, `tre_han = TRUE`; thực tập: nhập `thong_tin_noi_thuc_tap` + bản scan giấy xác nhận | minh_chung, tep_dinh_kem, thong_tin_noi_thuc_tap |
| UC17 | Nhận xét minh chứng | HD | Có lần nộp | Lưu `nhan_xet_minh_chung`; minh chứng → CO_NHAN_XET; thông báo SV | nhan_xet_minh_chung |
| UC18 | Theo dõi tiến độ của khoa | TKhoa | — | Bảng hồ sơ có lọc, cờ "Quá mốc/Nộp trễ", chọn nhiều để "Nhắc hàng loạt" | ho_so, minh_chung, thong_bao |
| UC19 | Nộp báo cáo hoặc khóa luận cuối | SV | Hồ sơ DANG_THUC_HIEN; mốc báo cáo cuối mở | `minh_chung` loai BAO_CAO_CUOI; ho_so → CHAM_HUONG_DAN; chọn hồ sơ cần xác minh (8.3); thông báo HD | minh_chung, xac_minh_noi_thuc_tap |
| UC20 | Nhập điểm nơi thực tập | HD | Hồ sơ CHAM_HUONG_DAN; đợt thực tập | Bắt buộc tick "đã đối chiếu bản gốc" (có ngày) trước khi nhập điểm; lưu `diem_thanh_phan` NOI_THUC_TAP | diem_thanh_phan, xac_minh_noi_thuc_tap |
| UC31 | Xác minh điểm với nơi thực tập | HD | «extend» UC20; `can_xac_minh = TRUE` | Ghi kết quả DA_XAC_MINH/NGHI_VAN + ngày + ghi chú; NGHI_VAN → thông báo TKhoa và cờ ở tổng hợp | xac_minh_noi_thuc_tap |
| UC21 | Chấm điểm hướng dẫn | HD | Hồ sơ CHAM_HUONG_DAN | `diem_thanh_phan` HUONG_DAN; "Lưu nháp" (NHAP) rồi "Gửi điểm" (DA_GUI, khóa) → ho_so CHO_PHAN_BIEN | diem_thanh_phan |
| UC22 | Phân công phản biện hoặc hội đồng | TKhoa | Hồ sơ CHO_PHAN_BIEN | Phản biện: chọn giảng viên khác HD, cùng khoa. Hội đồng: tạo hội đồng, thành viên, buổi bảo vệ, gán hồ sơ. Thông báo người chấm | phan_cong_cham, hoi_dong, thanh_vien_hoi_dong, buoi_bao_ve |
| UC23 | Nhận xét và chấm điểm phản biện | PB | Có phân công | `diem_thanh_phan` PHAN_BIEN (nháp → gửi) | diem_thanh_phan |
| UC24 | Chấm điểm và nhận xét tại hội đồng | HĐ | Có phân công hội đồng | Chọn buổi → sinh viên → chấm; **mỗi thành viên một dòng điểm** `HOI_DONG` | diem_thanh_phan |
| UC25 | Tổng hợp điểm và lưu hồ sơ | TKhoa | «include» UC26 | Bảng điểm; hồ sơ thiếu điểm bị chặn và chỉ rõ thiếu gì; chốt hàng loạt → `ket_qua_ho_so`, ho_so HOAN_TAT | ket_qua_ho_so, ho_so |
| UC26 | Tính điểm cuối theo trọng số | Hệ thống | Gọi từ UC25 | Điểm cuối theo mục 8.2 | dot_trong_so, diem_thanh_phan |
| UC27 | Xem kết quả | SV | Hồ sơ HOAN_TAT | Điểm từng phần, điểm cuối, trọng số đã dùng, nhận xét | ket_qua_ho_so, diem_thanh_phan |
| UC28 | Quản lý tài khoản và phân quyền | QT | — | Thêm/khóa/mở người dùng, gán vai trò theo khoa + hiệu lực, duyệt liên kết Google (dự phòng) | nguoi_dung, nguoi_dung_vai_tro, tai_khoan_lien_ket |
| UC29 | Quản lý danh mục khoa và bộ môn | QT | — | Thêm, sửa, ngừng sử dụng (không xóa nếu đã có dữ liệu liên quan) | khoa, bo_mon |
| UC30 | Xem nhật ký hệ thống | QT | — | Bảng lọc theo người, hành động, thời gian; chỉ xem; không hiện giá trị điểm | nhat_ky_he_thong |

---

## 7. Quy tắc nghiệp vụ

| Mã | Quy tắc | Cài ở |
|---|---|---|
| BR01 | Mỗi khoa chỉ thấy dữ liệu khoa mình | selector `for_user`, mọi view |
| BR02 | Mỗi sinh viên chỉ có **một hồ sơ trong một đợt** | `UNIQUE(dot_id, sinh_vien_id)` |
| BR03 | Sinh viên không nhập, không sửa điểm | quyền view + model |
| BR04 | Chỉ TKhoa xem `diem_dau_vao`; không lấy điểm rèn luyện/điểm từng môn | selector + adapter |
| BR05 | Điểm TB lấy **một lần** khi chốt danh sách, ghi `ngay_lay`; lấy lại phải xác nhận và tạo `lan_lay_diem` mới | service |
| BR06 | Không có điểm → nhóm "chưa có điểm", chia ngẫu nhiên đều | thuật toán 8.1 |
| BR07 | Giảng viên không vượt `dot.so_sv_toi_da_moi_gv` (tính cả dòng NHAP/CHO_XAC_NHAN/DONG_Y) | service + kiểm tra khi lưu nháp và khi HD đồng ý |
| BR08 | HD từ chối phải có lý do; hồ sơ về TRONG_DANH_SACH; TKhoa phân lại | service |
| BR09 | Chỉ công bố khi mọi dòng hiệu lực DONG_Y và không còn hồ sơ chưa giao | guard CONG_BO |
| BR10 | Sinh viên chỉ thấy GVHD sau khi ban phân công `DA_CONG_BO`; `ho_so.giang_vien_huong_dan_id` chỉ gán lúc công bố | service + selector |
| BR11 | Mỗi hồ sơ có tối đa **một** dòng `phan_cong_huong_dan` hiệu lực (không tính TU_CHOI, DA_THAY_THE) | chỉ mục UNIQUE một phần |
| BR12 | Mỗi hồ sơ có tối đa **một** đề tài ở CHO_CHOT hoặc DA_CHOT; lần bị TRA_LAI giữ làm lịch sử | chỉ mục UNIQUE một phần |
| BR13 | Đề tài chọn từ gợi ý phải còn chỗ (`so_luong_toi_da`) | service |
| BR14 | Trả lại đề tài bắt buộc có góp ý | form + service |
| BR15 | Nộp trễ vẫn nhận, gắn `tre_han = TRUE` (so `han_cuoi` của mốc) | service |
| BR16 | Tệp tải lên: kiểm tra phần mở rộng và dung lượng theo cấu hình; không thực thi, phục vụ qua view có kiểm tra quyền | service + view |
| BR17 | Điểm trong khoảng 0–10, thang 10 | CHECK + form |
| BR18 | Điểm `DA_GUI` khóa; không sửa nếu không mở lại (chức năng mở lại **không** làm) | service |
| BR19 | Thực tập: HD phải tick "đã đối chiếu bản gốc" (có ngày) trước khi nhập điểm nơi thực tập và trước khi gửi điểm | guard |
| BR20 | Hồ sơ được chọn xác minh (ngẫu nhiên theo tỷ lệ cấu hình hoặc HD đánh dấu nghi vấn) phải có kết quả xác minh trước khi HD gửi điểm; NGHI_VAN → thông báo TKhoa và cờ | guard + thông báo |
| BR21 | Phản biện ≠ HD của hồ sơ đó; cùng khoa | kiểm tra trong service (+ trigger tùy chọn) |
| BR22 | `phan_cong_cham.loai = PHAN_BIEN` ⇒ có `giang_vien_id`, không `hoi_dong_id`; `HOI_DONG` ⇒ ngược lại | CHECK |
| BR23 | Tổng `dot_trong_so.trong_so` của đợt = 100 (chỉ tính thành phần áp dụng cho loại đợt) | form + service |
| BR24 | Không chốt điểm cuối nếu thiếu thành phần có trọng số > 0 | guard CHOT_HO_SO |
| BR25 | Điểm hội đồng của hồ sơ = trung bình điểm các thành viên đã gửi | mục 8.2 |
| BR26 | `ket_qua_ho_so.trong_so_su_dung` lưu ảnh chụp trọng số và điểm thành phần lúc chốt; đổi cấu hình sau không làm lệch kết quả cũ | service |
| BR27 | Hồ sơ HOAN_TAT chỉ xem | service |
| BR28 | Nhật ký ghi hành động quan trọng, **không** ghi giá trị điểm; chỉ thêm, không sửa/xóa | model (không có update/delete) |
| BR29 | Không lưu mật khẩu cổng ở bất kỳ đâu | review code |
| BR30 | Thông báo gắn đúng sự kiện và đúng đích bấm vào (mục 12) | service |

---

## 8. Thuật toán và quy tắc tính toán

### 8.1 Gợi ý chia đều theo điểm (UC08)

Mục tiêu: mỗi GVHD nhận số sinh viên gần bằng nhau (chênh ≤ 1) **và** có đủ giỏi, khá, yếu.

```
Đầu vào: hồ sơ chưa phân công H (kèm diem_tb_he4 hoặc None), giảng viên G (thứ tự cố định),
         dung lượng còn lại của mỗi g: cap[g] = so_sv_toi_da_moi_gv - số đã nhận (mọi dòng hiệu lực)
Kiểm tra: |H| <= tổng cap, nếu không → báo lỗi "Thiếu chỗ: cần X, còn Y".
1. Tách H thành H_co_diem và H_chua_co_diem.
2. Sắp H_co_diem giảm dần theo diem_tb_he4 (hòa điểm: theo tin_chi_tich_luy giảm, rồi ma_sinh_vien).
3. Chia vòng kiểu rắn (snake): vòng 1 đi g1→gN, vòng 2 đi gN→g1, lặp lại; bỏ qua g đã hết cap.
4. H_chua_co_diem: xáo trộn ngẫu nhiên (seed ghi lại), rồi gán lần lượt cho giảng viên đang có ít sinh viên nhất
   (hòa thì theo thứ tự G), bỏ qua g hết cap.
5. Mỗi cặp (hồ sơ, g) sinh một dòng phan_cong_huong_dan trạng thái NHAP, la_goi_y = TRUE.
Đầu ra: danh sách dòng nháp; TKhoa chỉnh tay (khi chỉnh, la_goi_y = FALSE).
```
Không xét chuyên môn của giảng viên (trưởng khoa chỉnh tay). Phải có test: số lượng chênh ≤ 1; trung bình điểm của các giảng viên gần nhau; tôn trọng hạn mức; xử lý hết chỗ.

### 8.2 Tính điểm cuối (UC26)

```
Thành phần áp dụng của đợt = các dòng dot_trong_so có trong_so > 0.
Với mỗi thành phần T:
  - HUONG_DAN, NOI_THUC_TAP, PHAN_BIEN: điểm = diem_thanh_phan (DA_GUI) tương ứng (một người chấm)
  - HOI_DONG: điểm = trung bình điểm các thành viên đã DA_GUI
Hồ sơ "đủ điểm" khi mọi T áp dụng đều có điểm DA_GUI (với HOI_DONG: đủ mọi thành viên được phân).
diem_cuoi = Σ (diem_T × trong_so_T) / 100
Làm tròn: 2 chữ số thập phân (ASSUMPTION; quy tắc làm tròn chờ thầy; để thành hằng cấu hình).
Thiếu điểm → trả danh sách thiếu (thành phần + người chấm), không tính, không cho chốt.
```

### 8.3 Chọn hồ sơ cần xác minh nơi thực tập (UC31)

Chỉ đợt thực tập. Khi SV nộp báo cáo cuối (UC19), chọn **một lần** (xác định theo seed = `ho_so.id`, không lật lại được): `can_xac_minh = TRUE` với xác suất `XAC_MINH_TY_LE` (mặc định 0.10, ASSUMPTION), `ly_do_can_xac_minh = NGAU_NHIEN`. HD cũng có thể tự đánh dấu nghi vấn (`NGHI_VAN`) bất kỳ lúc nào.

### 8.4 Nhập danh sách Excel (UC04, UC05)

- Cột bắt buộc: `Mã sinh viên`, `Họ tên`; tùy chọn: `Lớp`, `Điểm TB` (chỉ dùng cho phương án dự phòng). Nhận diện cột theo tiêu đề (không phân biệt hoa thường, bỏ dấu), không theo vị trí cứng.
- Mỗi dòng: `HOP_LE`, `TRUNG` (trùng trong file hoặc đã có hồ sơ trong đợt), `LOI` (thiếu mã, sai định dạng, khác khoa). Dòng lỗi lên đầu bảng xem trước.
- Xác nhận chỉ cho phép khi không còn dòng `LOI`/`TRUNG` chưa xử lý.
- Xác nhận trong **một transaction**: tạo/ cập nhật `nguoi_dung` (CHUA_KICH_HOAT) + `sinh_vien` + `ho_so`.

---

## 9. Tích hợp USMART (qua adapter)

**Trạng thái:** tích hợp là **giả định chờ nhà trường đồng ý**. Giao thức thật (SSO/OAuth/API điểm) **chưa biết**. Vì vậy cài **interface**, không gọi trực tiếp.

```python
# integrations/usmart/base.py
class UsmartClient(Protocol):
    def build_login_redirect(self, state: str) -> str: ...
    def handle_login_callback(self, params: dict) -> Identity: ...      # ma_dinh_danh, ho_ten, email
    def get_gpa(self, ma_sinh_vien: list[str]) -> dict[str, GpaRecord | None]: ...
        # GpaRecord(diem_tb_he4: Decimal, tin_chi_tich_luy: int); None nếu thiếu
```

- `MockUsmartClient` (dùng khi `USMART_MODE=mock`): trang đăng nhập giả chọn người dùng mẫu (chỉ bật khi `DEBUG=True`), điểm sinh từ file `fixtures/usmart_gpa.json`. **Mọi phát triển và demo dùng mock.**
- `RealUsmartClient` (`USMART_MODE=real`): để trống (`NotImplementedError`) cho tới khi có tài liệu từ nhà trường.
- **Phương án dự phòng nếu không tích hợp được** (không đổi cấu trúc bảng): đăng nhập Google (`nha_cung_cap = GOOGLE`, `trang_thai_duyet = CHO_DUYET` rồi TKhoa duyệt liên kết mã sinh viên); điểm lấy từ cột `Điểm TB` trong file danh sách (`diem_dau_vao.nguon = FILE`).
- Chỉ lấy `diem_tb_he4` và `tin_chi_tich_luy`. Không lấy gì khác. Không bao giờ nhận hay lưu mật khẩu cổng: sinh viên nhập mật khẩu **trực tiếp trên USMART**.

---

## 10. Cơ sở dữ liệu

PostgreSQL. 33 bảng, 8 nhóm. **Quy ước:** mọi bảng có `id BIGINT` khóa chính tự tăng (Django `BigAutoField`); tên bảng và cột đúng như dưới đây (đặt `db_table`/`db_column` nếu tên model Python khác). Model Python đặt `PascalCase` tương ứng (ví dụ `ho_so` → `HoSo`). Cột "Ràng buộc" có `UNIQUE(a, b)` nghĩa là ràng buộc nhiều cột (dùng `Meta.constraints`). Thời gian dùng `TIMESTAMPTZ`.

### 10.1 Danh sách bảng theo nhóm

| STT | Bảng | Nhóm | Mục đích | UC |
|---|---|---|---|---|
| 1 | `khoa` | A. Tổ chức và người dùng | Danh mục khoa của trường (phạm vi dữ liệu theo khoa) | UC29 |
| 2 | `bo_mon` | A. Tổ chức và người dùng | Danh mục bộ môn thuộc khoa | UC29 |
| 3 | `nguoi_dung` | A. Tổ chức và người dùng | Tài khoản dùng chung cho mọi người dùng; không lưu mật khẩu cổng | UC01, UC28 |
| 4 | `tai_khoan_lien_ket` | A. Tổ chức và người dùng | Liên kết tài khoản hệ thống với danh tính ở bên ngoài (USMART, Google) | UC01 |
| 5 | `sinh_vien` | A. Tổ chức và người dùng | Thông tin riêng của sinh viên; được tạo khi nhập danh sách, trước lần đăng nhập đầu | UC01, UC04, UC05 |
| 6 | `giang_vien` | A. Tổ chức và người dùng | Thông tin riêng của giảng viên (dùng chung cho vai trò HD, PB, HĐ) | UC10, UC22 |
| 7 | `vai_tro` | A. Tổ chức và người dùng | Danh mục vai trò hệ thống | UC28 |
| 8 | `nguoi_dung_vai_tro` | A. Tổ chức và người dùng | Gán vai trò cho người dùng, giới hạn theo khoa | UC28 |
| 9 | `dot` | B. Đợt và cấu hình | Một đợt thực tập hoặc đồ án tốt nghiệp của một khoa | UC03 |
| 10 | `dot_moc_thoi_gian` | B. Đợt và cấu hình | Các mốc thời gian của đợt (nộp minh chứng, nộp báo cáo, chấm điểm…) | UC03, UC16, UC18 |
| 11 | `dot_trong_so` | B. Đợt và cấu hình | Trọng số các thành phần điểm của đợt | UC03, UC26 |
| 12 | `lan_nhap_danh_sach` | C. Danh sách và điểm đầu vào | Mỗi lần tải file danh sách của Phòng đào tạo lên hệ thống | UC04, UC05 |
| 13 | `dong_nhap_danh_sach` | C. Danh sách và điểm đầu vào | Từng dòng bóc tách từ file, dùng cho bước xem trước và xác nhận | UC05 |
| 14 | `ho_so` | C. Danh sách và điểm đầu vào | Hồ sơ của một sinh viên trong một đợt; bảng trung tâm theo dõi vòng đời | UC05–UC27 |
| 15 | `diem_dau_vao` | C. Danh sách và điểm đầu vào | Điểm TB tích lũy dùng để gợi ý chia đều; tách bảng để chỉ TKhoa được xem | UC06, UC08 |
| 16 | `lan_lay_diem` | C. Danh sách và điểm đầu vào | Nhật ký mỗi lần lấy điểm TB từ USMART (một lần khi chốt danh sách) | UC06 |
| 17 | `ban_phan_cong` | D. Phân công hướng dẫn | Bản phân công hướng dẫn của một đợt (nháp → gửi → công bố) | UC07, UC09 |
| 18 | `phan_cong_huong_dan` | D. Phân công hướng dẫn | Từng dòng phân công một hồ sơ cho một giảng viên và phản hồi của HD | UC07, UC08, UC10, UC11 |
| 19 | `de_tai_goi_y` | E. Đề tài | Đề tài do giảng viên đưa ra để sinh viên chọn | UC12, UC13 |
| 20 | `de_tai` | E. Đề tài | Đề tài của một hồ sơ (chọn từ gợi ý hoặc sinh viên đề xuất) và kết quả chốt | UC13, UC14, UC15 |
| 21 | `thong_tin_noi_thuc_tap` | F. Thực hiện và minh chứng | Thông tin liên hệ nơi thực tập, dùng để xác minh điểm nơi thực tập | UC16, UC31 |
| 22 | `minh_chung` | F. Thực hiện và minh chứng | Mỗi lần sinh viên nộp minh chứng tiến độ, báo cáo cuối hoặc giấy xác nhận | UC16, UC17, UC19 |
| 23 | `tep_dinh_kem` | F. Thực hiện và minh chứng | Tệp thuộc một lần nộp minh chứng (báo cáo, sản phẩm, bản scan giấy xác nhận) | UC16, UC19 |
| 24 | `nhan_xet_minh_chung` | F. Thực hiện và minh chứng | Nhận xét của HD cho từng lần nộp | UC17 |
| 25 | `hoi_dong` | G. Chấm điểm và kết quả | Hội đồng chấm đồ án tốt nghiệp | UC22, UC24 |
| 26 | `thanh_vien_hoi_dong` | G. Chấm điểm và kết quả | Giảng viên là thành viên của hội đồng | UC22, UC24 |
| 27 | `buoi_bao_ve` | G. Chấm điểm và kết quả | Buổi bảo vệ của một hội đồng (một hội đồng có thể có nhiều buổi) | UC22, UC24 |
| 28 | `phan_cong_cham` | G. Chấm điểm và kết quả | Phân công phản biện hoặc hội đồng cho từng hồ sơ | UC22 |
| 29 | `diem_thanh_phan` | G. Chấm điểm và kết quả | Điểm của từng thành phần do người chấm nhập | UC20, UC21, UC23, UC24 |
| 30 | `xac_minh_noi_thuc_tap` | G. Chấm điểm và kết quả | Đối chiếu bản gốc và xác minh điểm nơi thực tập (chống giả mạo) | UC20, UC31 |
| 31 | `ket_qua_ho_so` | G. Chấm điểm và kết quả | Điểm cuối và việc lưu hồ sơ | UC25, UC26, UC27 |
| 32 | `thong_bao` | H. Hệ thống | Thông báo gửi đến người dùng | UC02 |
| 33 | `nhat_ky_he_thong` | H. Hệ thống | Nhật ký hành động quan trọng; chỉ thêm, không sửa; không ghi nội dung điểm | UC30 |


### 10.2 Chi tiết từng bảng

#### Nhóm A. Tổ chức và người dùng

##### 1. `khoa`

Danh mục khoa của trường (phạm vi dữ liệu theo khoa). UC: UC29.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `ma_khoa` | VARCHAR(20) | NOT NULL, UNIQUE | Mã khoa |
| `ten_khoa` | VARCHAR(200) | NOT NULL | Tên khoa |
| `dang_hoat_dong` | BOOLEAN | NOT NULL, mặc định TRUE | Còn sử dụng hay không |

##### 2. `bo_mon`

Danh mục bộ môn thuộc khoa. UC: UC29.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `khoa_id` | BIGINT | FK → khoa.id, NOT NULL | Khoa chủ quản |
| `ma_bo_mon` | VARCHAR(20) | NOT NULL, UNIQUE(khoa_id, ma_bo_mon) | Mã bộ môn |
| `ten_bo_mon` | VARCHAR(200) | NOT NULL | Tên bộ môn |
| `dang_hoat_dong` | BOOLEAN | NOT NULL, mặc định TRUE | Còn sử dụng hay không |

##### 3. `nguoi_dung`

Tài khoản dùng chung cho mọi người dùng; không lưu mật khẩu cổng. UC: UC01, UC28.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `ma_dinh_danh_cong` | VARCHAR(50) | NOT NULL, UNIQUE | Mã đăng nhập trên cổng (USMART): mã sinh viên hoặc mã cán bộ |
| `ho_ten` | VARCHAR(150) | NOT NULL | Họ và tên |
| `email` | VARCHAR(150) | UNIQUE, NULL | Email liên hệ |
| `so_dien_thoai` | VARCHAR(20) | NULL | Số điện thoại |
| `loai_nguoi_dung` | VARCHAR(20) | NOT NULL, CHECK | SINH_VIEN / GIANG_VIEN / QUAN_TRI |
| `trang_thai` | VARCHAR(20) | NOT NULL, CHECK | CHUA_KICH_HOAT / HOAT_DONG / KHOA |
| `lan_dang_nhap_cuoi` | TIMESTAMPTZ | NULL | Lần đăng nhập gần nhất |
| `ngay_tao` | TIMESTAMPTZ | NOT NULL, mặc định now() | Ngày tạo |

##### 4. `tai_khoan_lien_ket`

Liên kết tài khoản hệ thống với danh tính ở bên ngoài (USMART, Google). UC: UC01.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `nguoi_dung_id` | BIGINT | FK → nguoi_dung.id, NOT NULL | Người dùng |
| `nha_cung_cap` | VARCHAR(20) | NOT NULL, CHECK | USMART / GOOGLE |
| `ma_ngoai` | VARCHAR(100) | NOT NULL, UNIQUE(nha_cung_cap, ma_ngoai) | Mã định danh phía nhà cung cấp |
| `email` | VARCHAR(150) | NULL | Email phía nhà cung cấp |
| `trang_thai_duyet` | VARCHAR(20) | NOT NULL, CHECK | TU_DONG / CHO_DUYET / DA_DUYET / TU_CHOI (phương án dự phòng Google do TKhoa duyệt liên kết MSSV) |
| `ngay_lien_ket` | TIMESTAMPTZ | NOT NULL | Ngày liên kết |

##### 5. `sinh_vien`

Thông tin riêng của sinh viên; được tạo khi nhập danh sách, trước lần đăng nhập đầu. UC: UC01, UC04, UC05.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `nguoi_dung_id` | BIGINT | FK → nguoi_dung.id, UNIQUE, NOT NULL | Tài khoản tương ứng |
| `ma_sinh_vien` | VARCHAR(20) | NOT NULL, UNIQUE | Mã sinh viên |
| `lop` | VARCHAR(50) | NULL | Lớp sinh hoạt |
| `khoa_id` | BIGINT | FK → khoa.id, NOT NULL | Khoa của sinh viên |

##### 6. `giang_vien`

Thông tin riêng của giảng viên (dùng chung cho vai trò HD, PB, HĐ). UC: UC10, UC22.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `nguoi_dung_id` | BIGINT | FK → nguoi_dung.id, UNIQUE, NOT NULL | Tài khoản tương ứng |
| `ma_can_bo` | VARCHAR(20) | NOT NULL, UNIQUE | Mã cán bộ |
| `khoa_id` | BIGINT | FK → khoa.id, NOT NULL | Khoa công tác |
| `bo_mon_id` | BIGINT | FK → bo_mon.id, NULL | Bộ môn |
| `hoc_vi` | VARCHAR(50) | NULL | Học vị, học hàm |

##### 7. `vai_tro`

Danh mục vai trò hệ thống. UC: UC28.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `ma_vai_tro` | VARCHAR(20) | NOT NULL, UNIQUE | TRUONG_KHOA / GIANG_VIEN / QUAN_TRI (SV xác định qua bảng sinh_vien) |
| `ten_vai_tro` | VARCHAR(100) | NOT NULL | Tên hiển thị |
| `mo_ta` | VARCHAR(300) | NULL | Mô tả |

##### 8. `nguoi_dung_vai_tro`

Gán vai trò cho người dùng, giới hạn theo khoa. UC: UC28.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `nguoi_dung_id` | BIGINT | FK → nguoi_dung.id, NOT NULL | Người dùng |
| `vai_tro_id` | BIGINT | FK → vai_tro.id, NOT NULL | Vai trò |
| `khoa_id` | BIGINT | FK → khoa.id, NULL | Phạm vi khoa (NULL với quản trị) |
| `hieu_luc_tu` | DATE | NOT NULL | Ngày bắt đầu hiệu lực |
| `hieu_luc_den` | DATE | NULL | Ngày hết hiệu lực; UNIQUE(nguoi_dung_id, vai_tro_id, khoa_id) |

#### Nhóm B. Đợt và cấu hình

##### 9. `dot`

Một đợt thực tập hoặc đồ án tốt nghiệp của một khoa. UC: UC03.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `ma_dot` | VARCHAR(30) | NOT NULL, UNIQUE | Mã đợt |
| `ten_dot` | VARCHAR(200) | NOT NULL | Tên đợt |
| `loai` | VARCHAR(20) | NOT NULL, CHECK | THUC_TAP / DO_AN |
| `hoc_ky` | SMALLINT | NOT NULL, CHECK 1..3 | Học kỳ |
| `nam_hoc` | VARCHAR(9) | NOT NULL | Ví dụ 2026-2027 |
| `khoa_id` | BIGINT | FK → khoa.id, NOT NULL | Khoa sở hữu đợt |
| `trang_thai` | VARCHAR(20) | NOT NULL, CHECK | CHUAN_BI / PHAN_CONG / CHOT_DE_TAI / THUC_HIEN / CHAM_DIEM / HOAN_TAT |
| `so_sv_toi_da_moi_gv` | SMALLINT | NOT NULL, CHECK > 0 | Hạn mức sinh viên tối đa cho mỗi giảng viên hướng dẫn |
| `hinh_thuc_cham` | VARCHAR(20) | NOT NULL, CHECK | PHAN_BIEN / HOI_DONG (HOI_DONG chỉ cho đồ án) |
| `nguoi_tao_id` | BIGINT | FK → nguoi_dung.id, NOT NULL | Người mở đợt |
| `ngay_tao` | TIMESTAMPTZ | NOT NULL, mặc định now() | Ngày tạo |

##### 10. `dot_moc_thoi_gian`

Các mốc thời gian của đợt (nộp minh chứng, nộp báo cáo, chấm điểm…). UC: UC03, UC16, UC18.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `dot_id` | BIGINT | FK → dot.id, NOT NULL | Đợt |
| `ma_moc` | VARCHAR(30) | NOT NULL, UNIQUE(dot_id, ma_moc) | Mã mốc |
| `ten_moc` | VARCHAR(150) | NOT NULL | Tên mốc |
| `loai_moc` | VARCHAR(20) | NOT NULL, CHECK | PHAN_CONG / CHOT_DE_TAI / NOP_TIEN_DO / NOP_BAO_CAO / CHAM_DIEM |
| `thu_tu` | SMALLINT | NOT NULL | Thứ tự trong đợt |
| `han_cuoi` | TIMESTAMPTZ | NOT NULL | Hạn cuối của mốc |

##### 11. `dot_trong_so`

Trọng số các thành phần điểm của đợt. UC: UC03, UC26.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `dot_id` | BIGINT | FK → dot.id, NOT NULL | Đợt |
| `thanh_phan` | VARCHAR(20) | NOT NULL, CHECK, UNIQUE(dot_id, thanh_phan) | HUONG_DAN / NOI_THUC_TAP / PHAN_BIEN / HOI_DONG |
| `trong_so` | NUMERIC(5,2) | NOT NULL, CHECK 0..100 | Trọng số (%); tổng các dòng của đợt = 100 (kiểm tra ở tầng ứng dụng khi lưu cấu hình) |

#### Nhóm C. Danh sách và điểm đầu vào

##### 12. `lan_nhap_danh_sach`

Mỗi lần tải file danh sách của Phòng đào tạo lên hệ thống. UC: UC04, UC05.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `dot_id` | BIGINT | FK → dot.id, NOT NULL | Đợt |
| `nguoi_tai_id` | BIGINT | FK → nguoi_dung.id, NOT NULL | Người tải file (TKhoa) |
| `ten_tep` | VARCHAR(255) | NOT NULL | Tên file gốc |
| `duong_dan` | VARCHAR(500) | NOT NULL | Đường dẫn lưu file |
| `tong_dong` | INTEGER | NOT NULL, mặc định 0 | Tổng số dòng đọc được |
| `dong_hop_le` | INTEGER | NOT NULL, mặc định 0 | Số dòng hợp lệ |
| `dong_loi` | INTEGER | NOT NULL, mặc định 0 | Số dòng lỗi |
| `trang_thai` | VARCHAR(20) | NOT NULL, CHECK | XEM_TRUOC / DA_XAC_NHAN / HUY |
| `ngay_tai` | TIMESTAMPTZ | NOT NULL, mặc định now() | Ngày tải |

##### 13. `dong_nhap_danh_sach`

Từng dòng bóc tách từ file, dùng cho bước xem trước và xác nhận. UC: UC05.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `lan_nhap_id` | BIGINT | FK → lan_nhap_danh_sach.id, NOT NULL | Lần nhập |
| `so_dong` | INTEGER | NOT NULL | Số thứ tự dòng trong file |
| `ma_sinh_vien` | VARCHAR(20) | NOT NULL | Mã sinh viên đọc được |
| `ho_ten` | VARCHAR(150) | NULL | Họ tên |
| `lop` | VARCHAR(50) | NULL | Lớp |
| `diem_tb` | NUMERIC(4,2) | NULL | Điểm trong file (chỉ dùng cho phương án dự phòng) |
| `trang_thai_dong` | VARCHAR(20) | NOT NULL, CHECK | HOP_LE / TRUNG / LOI |
| `loi` | VARCHAR(300) | NULL | Mô tả lỗi (sai mã, trùng, khác khoa…) |

##### 14. `ho_so`

Hồ sơ của một sinh viên trong một đợt; bảng trung tâm theo dõi vòng đời. UC: UC05–UC27.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `dot_id` | BIGINT | FK → dot.id, NOT NULL | Đợt |
| `sinh_vien_id` | BIGINT | FK → sinh_vien.id, NOT NULL | Sinh viên; UNIQUE(dot_id, sinh_vien_id) |
| `trang_thai` | VARCHAR(25) | NOT NULL, CHECK | TRONG_DANH_SACH / CHO_XAC_NHAN / CHO_CHOT_DE_TAI / DANG_THUC_HIEN / CHAM_HUONG_DAN / CHO_PHAN_BIEN / HOAN_TAT |
| `giang_vien_huong_dan_id` | BIGINT | FK → giang_vien.id, NULL | HD hiện tại; gán khi công bố, từ dòng phân công đã DONG_Y |
| `de_tai_hien_tai_id` | BIGINT | FK → de_tai.id, NULL | Đề tài đã chốt |
| `ngay_tao` | TIMESTAMPTZ | NOT NULL, mặc định now() | Ngày tạo |
| `ngay_cap_nhat` | TIMESTAMPTZ | NOT NULL | Lần đổi trạng thái gần nhất |

##### 15. `diem_dau_vao`

Điểm TB tích lũy dùng để gợi ý chia đều; tách bảng để chỉ TKhoa được xem. UC: UC06, UC08.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `ho_so_id` | BIGINT | FK → ho_so.id, UNIQUE, NOT NULL | Hồ sơ |
| `diem_tb_he4` | NUMERIC(3,2) | NULL, CHECK 0..4 | Điểm TB tích lũy hệ 4 |
| `tin_chi_tich_luy` | SMALLINT | NULL | Số tín chỉ tích lũy |
| `ngay_lay` | TIMESTAMPTZ | NULL | Ngày lấy điểm |
| `nguon` | VARCHAR(20) | NOT NULL, CHECK | USMART / FILE / KHONG_CO (KHONG_CO → nhóm chưa có điểm) |

##### 16. `lan_lay_diem`

Nhật ký mỗi lần lấy điểm TB từ USMART (một lần khi chốt danh sách). UC: UC06.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `dot_id` | BIGINT | FK → dot.id, NOT NULL | Đợt |
| `nguoi_thuc_hien_id` | BIGINT | FK → nguoi_dung.id, NOT NULL | Người thực hiện |
| `nguon` | VARCHAR(20) | NOT NULL, CHECK | USMART / FILE |
| `ngay_lay` | TIMESTAMPTZ | NOT NULL, mặc định now() | Thời điểm lấy |
| `so_sv_co_diem` | INTEGER | NOT NULL | Số SV lấy được điểm |
| `so_sv_thieu` | INTEGER | NOT NULL | Số SV không có điểm |
| `trang_thai` | VARCHAR(20) | NOT NULL, CHECK | THANH_CONG / MOT_PHAN / LOI |
| `chi_tiet_loi` | TEXT | NULL | Thông tin lỗi nếu có |

#### Nhóm D. Phân công hướng dẫn

##### 17. `ban_phan_cong`

Bản phân công hướng dẫn của một đợt (nháp → gửi → công bố). UC: UC07, UC09.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `dot_id` | BIGINT | FK → dot.id, NOT NULL | Đợt |
| `trang_thai` | VARCHAR(20) | NOT NULL, CHECK | NHAP / DA_GUI / DA_CONG_BO |
| `nguoi_tao_id` | BIGINT | FK → nguoi_dung.id, NOT NULL | TKhoa soạn |
| `ngay_gui` | TIMESTAMPTZ | NULL | Ngày gửi cho giảng viên |
| `ngay_cong_bo` | TIMESTAMPTZ | NULL | Ngày công bố chính thức |

##### 18. `phan_cong_huong_dan`

Từng dòng phân công một hồ sơ cho một giảng viên và phản hồi của HD. UC: UC07, UC08, UC10, UC11.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `ban_phan_cong_id` | BIGINT | FK → ban_phan_cong.id, NOT NULL | Bản phân công |
| `ho_so_id` | BIGINT | FK → ho_so.id, NOT NULL | Hồ sơ |
| `giang_vien_id` | BIGINT | FK → giang_vien.id, NOT NULL | Giảng viên được phân |
| `trang_thai` | VARCHAR(20) | NOT NULL, CHECK | NHAP / CHO_XAC_NHAN / DONG_Y / TU_CHOI / DA_THAY_THE (đổi HD sau công bố, dòng cũ giữ làm lịch sử) |
| `la_goi_y` | BOOLEAN | NOT NULL, mặc định FALSE | TRUE nếu do gợi ý chia đều sinh ra và chưa chỉnh tay |
| `ly_do_tu_choi` | VARCHAR(500) | NULL | Bắt buộc khi TU_CHOI |
| `ly_do_thay_the` | VARCHAR(500) | NULL | Bắt buộc khi DA_THAY_THE |
| `ngay_phan_hoi` | TIMESTAMPTZ | NULL | Ngày HD phản hồi |

#### Nhóm E. Đề tài

##### 19. `de_tai_goi_y`

Đề tài do giảng viên đưa ra để sinh viên chọn. UC: UC12, UC13.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `dot_id` | BIGINT | FK → dot.id, NOT NULL | Đợt |
| `giang_vien_id` | BIGINT | FK → giang_vien.id, NOT NULL | Giảng viên đưa ra |
| `ten_de_tai` | VARCHAR(300) | NOT NULL | Tên đề tài |
| `mo_ta` | TEXT | NULL | Mô tả, yêu cầu |
| `so_luong_toi_da` | SMALLINT | NOT NULL, mặc định 1 | Số sinh viên có thể chọn |
| `trang_thai` | VARCHAR(10) | NOT NULL, CHECK | MO / DONG |

##### 20. `de_tai`

Đề tài của một hồ sơ (chọn từ gợi ý hoặc sinh viên đề xuất) và kết quả chốt. UC: UC13, UC14, UC15.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `ho_so_id` | BIGINT | FK → ho_so.id, NOT NULL | Hồ sơ |
| `nguon` | VARCHAR(20) | NOT NULL, CHECK | GV_DUA_RA / SV_DE_XUAT |
| `de_tai_goi_y_id` | BIGINT | FK → de_tai_goi_y.id, NULL | Bắt buộc khi nguon = GV_DUA_RA |
| `ten_de_tai` | VARCHAR(300) | NOT NULL | Tên đề tài |
| `mo_ta` | TEXT | NULL | Mô tả |
| `trang_thai` | VARCHAR(15) | NOT NULL, CHECK | CHO_CHOT / DA_CHOT / TRA_LAI |
| `gop_y_cua_gv` | VARCHAR(1000) | NULL | Lý do trả lại, yêu cầu chỉnh sửa |
| `ngay_gui` | TIMESTAMPTZ | NOT NULL | Ngày sinh viên gửi |
| `ngay_chot` | TIMESTAMPTZ | NULL | Ngày HD chốt |

#### Nhóm F. Thực hiện và minh chứng

##### 21. `thong_tin_noi_thuc_tap`

Thông tin liên hệ nơi thực tập, dùng để xác minh điểm nơi thực tập. UC: UC16, UC31.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `ho_so_id` | BIGINT | FK → ho_so.id, UNIQUE, NOT NULL | Hồ sơ |
| `ten_don_vi` | VARCHAR(200) | NOT NULL | Tên đơn vị |
| `nguoi_xac_nhan` | VARCHAR(150) | NOT NULL | Người ký xác nhận |
| `chuc_vu` | VARCHAR(100) | NULL | Chức vụ |
| `so_dien_thoai` | VARCHAR(20) | NULL | Số điện thoại |
| `email` | VARCHAR(150) | NULL | Email |
| `dia_chi` | VARCHAR(300) | NULL | Địa chỉ |

##### 22. `minh_chung`

Mỗi lần sinh viên nộp minh chứng tiến độ, báo cáo cuối hoặc giấy xác nhận. UC: UC16, UC17, UC19.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `ho_so_id` | BIGINT | FK → ho_so.id, NOT NULL | Hồ sơ |
| `moc_id` | BIGINT | FK → dot_moc_thoi_gian.id, NULL | Mốc tương ứng |
| `loai` | VARCHAR(20) | NOT NULL, CHECK | TIEN_DO / BAO_CAO_CUOI / GIAY_XAC_NHAN |
| `ghi_chu` | VARCHAR(1000) | NULL | Ghi chú của sinh viên |
| `ngay_nop` | TIMESTAMPTZ | NOT NULL, mặc định now() | Ngày nộp |
| `tre_han` | BOOLEAN | NOT NULL, mặc định FALSE | Nộp sau hạn của mốc |
| `trang_thai` | VARCHAR(15) | NOT NULL, CHECK | DA_NOP / CO_NHAN_XET |

##### 23. `tep_dinh_kem`

Tệp thuộc một lần nộp minh chứng (báo cáo, sản phẩm, bản scan giấy xác nhận). UC: UC16, UC19.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `minh_chung_id` | BIGINT | FK → minh_chung.id, NOT NULL | Lần nộp |
| `ten_tep` | VARCHAR(255) | NOT NULL | Tên file |
| `duong_dan` | VARCHAR(500) | NOT NULL | Đường dẫn lưu |
| `loai_mime` | VARCHAR(100) | NOT NULL | Kiểu tệp (kiểm tra danh sách cho phép) |
| `kich_thuoc` | BIGINT | NOT NULL, CHECK ≤ giới hạn | Kích thước (byte) |
| `nguoi_tai_id` | BIGINT | FK → nguoi_dung.id, NOT NULL | Người tải |
| `ngay_tai` | TIMESTAMPTZ | NOT NULL, mặc định now() | Ngày tải |

##### 24. `nhan_xet_minh_chung`

Nhận xét của HD cho từng lần nộp. UC: UC17.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `minh_chung_id` | BIGINT | FK → minh_chung.id, NOT NULL | Lần nộp |
| `giang_vien_id` | BIGINT | FK → giang_vien.id, NOT NULL | HD nhận xét |
| `noi_dung` | TEXT | NOT NULL | Nội dung nhận xét |
| `ngay_tao` | TIMESTAMPTZ | NOT NULL, mặc định now() | Ngày nhận xét |

#### Nhóm G. Chấm điểm và kết quả

##### 25. `hoi_dong`

Hội đồng chấm đồ án tốt nghiệp. UC: UC22, UC24.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `dot_id` | BIGINT | FK → dot.id, NOT NULL | Đợt |
| `ten_hoi_dong` | VARCHAR(150) | NOT NULL, UNIQUE(dot_id, ten_hoi_dong) | Tên hội đồng |
| `ghi_chu` | VARCHAR(300) | NULL | Ghi chú |

##### 26. `thanh_vien_hoi_dong`

Giảng viên là thành viên của hội đồng. UC: UC22, UC24.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `hoi_dong_id` | BIGINT | FK → hoi_dong.id, NOT NULL | Hội đồng |
| `giang_vien_id` | BIGINT | FK → giang_vien.id, NOT NULL | Thành viên; UNIQUE(hoi_dong_id, giang_vien_id) |
| `vai_tro_trong_hoi_dong` | VARCHAR(30) | NULL | Chủ tịch / thư ký / ủy viên (tùy chọn, chờ thầy xác nhận) |

##### 27. `buoi_bao_ve`

Buổi bảo vệ của một hội đồng (một hội đồng có thể có nhiều buổi). UC: UC22, UC24.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `hoi_dong_id` | BIGINT | FK → hoi_dong.id, NOT NULL | Hội đồng |
| `ten_buoi` | VARCHAR(100) | NOT NULL | Ví dụ: Buổi sáng 20/12 |
| `thoi_gian` | TIMESTAMPTZ | NOT NULL | Thời gian bắt đầu |
| `dia_diem` | VARCHAR(200) | NULL | Địa điểm |

##### 28. `phan_cong_cham`

Phân công phản biện hoặc hội đồng cho từng hồ sơ. UC: UC22.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `ho_so_id` | BIGINT | FK → ho_so.id, NOT NULL | Hồ sơ |
| `loai` | VARCHAR(15) | NOT NULL, CHECK | PHAN_BIEN / HOI_DONG |
| `giang_vien_id` | BIGINT | FK → giang_vien.id, NULL | Giảng viên phản biện; bắt buộc khi PHAN_BIEN, phải khác HD của hồ sơ |
| `hoi_dong_id` | BIGINT | FK → hoi_dong.id, NULL | Hội đồng; bắt buộc khi HOI_DONG |
| `buoi_bao_ve_id` | BIGINT | FK → buoi_bao_ve.id, NULL | Buổi bảo vệ của hồ sơ; có thể gán sau khi phân hội đồng, phải thuộc đúng hội đồng đó |
| `nguoi_phan_cong_id` | BIGINT | FK → nguoi_dung.id, NOT NULL | TKhoa thực hiện |
| `ngay_phan_cong` | TIMESTAMPTZ | NOT NULL, mặc định now() | Ngày phân công |

##### 29. `diem_thanh_phan`

Điểm của từng thành phần do người chấm nhập. UC: UC20, UC21, UC23, UC24.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `ho_so_id` | BIGINT | FK → ho_so.id, NOT NULL | Hồ sơ |
| `thanh_phan` | VARCHAR(20) | NOT NULL, CHECK | HUONG_DAN / NOI_THUC_TAP / PHAN_BIEN / HOI_DONG |
| `nguoi_cham_id` | BIGINT | FK → giang_vien.id, NOT NULL | Người chấm; UNIQUE(ho_so_id, thanh_phan, nguoi_cham_id) |
| `diem` | NUMERIC(4,2) | NULL, CHECK 0..10 | Điểm hệ 10; sinh viên không có quyền ghi |
| `nhan_xet` | TEXT | NULL | Nhận xét |
| `trang_thai` | VARCHAR(10) | NOT NULL, CHECK | NHAP / DA_GUI (DA_GUI không sửa nếu không mở lại) |
| `ngay_gui` | TIMESTAMPTZ | NULL | Ngày gửi điểm |

##### 30. `xac_minh_noi_thuc_tap`

Đối chiếu bản gốc và xác minh điểm nơi thực tập (chống giả mạo). UC: UC20, UC31.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `ho_so_id` | BIGINT | FK → ho_so.id, UNIQUE, NOT NULL | Hồ sơ |
| `da_doi_chieu_ban_goc` | BOOLEAN | NOT NULL, mặc định FALSE | HD đã đối chiếu bản gốc có dấu |
| `ngay_doi_chieu` | DATE | NULL | Ngày đối chiếu |
| `nguoi_doi_chieu_id` | BIGINT | FK → giang_vien.id, NULL | HD đối chiếu |
| `can_xac_minh` | BOOLEAN | NOT NULL, mặc định FALSE | Hồ sơ cần xác minh với đơn vị |
| `ly_do_can_xac_minh` | VARCHAR(15) | NULL, CHECK | NGAU_NHIEN / NGHI_VAN |
| `ket_qua_xac_minh` | VARCHAR(15) | NULL, CHECK | DA_XAC_MINH / NGHI_VAN |
| `ngay_xac_minh` | DATE | NULL | Ngày xác minh |
| `ghi_chu` | VARCHAR(1000) | NULL | Ghi chú (người liên hệ, cách xác minh) |

##### 31. `ket_qua_ho_so`

Điểm cuối và việc lưu hồ sơ. UC: UC25, UC26, UC27.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `ho_so_id` | BIGINT | FK → ho_so.id, UNIQUE, NOT NULL | Hồ sơ |
| `diem_cuoi` | NUMERIC(4,2) | NOT NULL, CHECK 0..10 | Điểm cuối theo trọng số |
| `trong_so_su_dung` | JSONB | NOT NULL | Ảnh chụp trọng số và điểm thành phần lúc chốt |
| `ngay_chot` | TIMESTAMPTZ | NOT NULL | Ngày chốt |
| `nguoi_chot_id` | BIGINT | FK → nguoi_dung.id, NOT NULL | TKhoa chốt |
| `da_luu_tru` | BOOLEAN | NOT NULL, mặc định TRUE | Đã lưu hồ sơ |

#### Nhóm H. Hệ thống

##### 32. `thong_bao`

Thông báo gửi đến người dùng. UC: UC02.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `nguoi_nhan_id` | BIGINT | FK → nguoi_dung.id, NOT NULL | Người nhận |
| `loai_su_kien` | VARCHAR(40) | NOT NULL | Ví dụ: CONG_BO_PHAN_CONG, DE_TAI_TRA_LAI, SAP_HET_HAN |
| `tieu_de` | VARCHAR(200) | NOT NULL | Tiêu đề |
| `noi_dung` | VARCHAR(1000) | NULL | Nội dung |
| `ho_so_id` | BIGINT | FK → ho_so.id, NULL | Hồ sơ liên quan |
| `da_doc` | BOOLEAN | NOT NULL, mặc định FALSE | Đã đọc |
| `ngay_tao` | TIMESTAMPTZ | NOT NULL, mặc định now() | Ngày tạo |

##### 33. `nhat_ky_he_thong`

Nhật ký hành động quan trọng; chỉ thêm, không sửa; không ghi nội dung điểm. UC: UC30.

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT | PK, tự tăng | Khóa chính |
| `nguoi_thuc_hien_id` | BIGINT | FK → nguoi_dung.id, NULL | Người thực hiện (NULL nếu hệ thống) |
| `hanh_dong` | VARCHAR(50) | NOT NULL | Ví dụ: MO_DOT, CONG_BO, CHOT_DIEM |
| `doi_tuong_loai` | VARCHAR(50) | NULL | Bảng đối tượng |
| `doi_tuong_id` | BIGINT | NULL | Khóa đối tượng |
| `mo_ta` | VARCHAR(500) | NULL | Mô tả ngắn (không chứa giá trị điểm) |
| `dia_chi_ip` | VARCHAR(45) | NULL | Địa chỉ IP |
| `ngay_thuc_hien` | TIMESTAMPTZ | NOT NULL, mặc định now() | Thời điểm |



### 10.3 Quan hệ giữa các bảng

Sinh từ các khóa ngoại ở 10.2 (1 – 1 là cột có `UNIQUE`).

| STT | Bảng cha | Bảng con | Loại | Khóa ngoại ở bảng con |
|---|---|---|---|---|
| 1 | `khoa` | `bo_mon` | 1 – N | `khoa_id` |
| 2 | `nguoi_dung` | `tai_khoan_lien_ket` | 1 – N | `nguoi_dung_id` |
| 3 | `nguoi_dung` | `sinh_vien` | 1 – 1 | `nguoi_dung_id` |
| 4 | `khoa` | `sinh_vien` | 1 – N | `khoa_id` |
| 5 | `nguoi_dung` | `giang_vien` | 1 – 1 | `nguoi_dung_id` |
| 6 | `khoa` | `giang_vien` | 1 – N | `khoa_id` |
| 7 | `bo_mon` | `giang_vien` | 1 – N | `bo_mon_id` (có thể rỗng) |
| 8 | `nguoi_dung` | `nguoi_dung_vai_tro` | 1 – N | `nguoi_dung_id` |
| 9 | `vai_tro` | `nguoi_dung_vai_tro` | 1 – N | `vai_tro_id` |
| 10 | `khoa` | `nguoi_dung_vai_tro` | 1 – N | `khoa_id` (có thể rỗng) |
| 11 | `khoa` | `dot` | 1 – N | `khoa_id` |
| 12 | `nguoi_dung` | `dot` | 1 – N | `nguoi_tao_id` |
| 13 | `dot` | `dot_moc_thoi_gian` | 1 – N | `dot_id` |
| 14 | `dot` | `dot_trong_so` | 1 – N | `dot_id` |
| 15 | `dot` | `lan_nhap_danh_sach` | 1 – N | `dot_id` |
| 16 | `nguoi_dung` | `lan_nhap_danh_sach` | 1 – N | `nguoi_tai_id` |
| 17 | `lan_nhap_danh_sach` | `dong_nhap_danh_sach` | 1 – N | `lan_nhap_id` |
| 18 | `dot` | `ho_so` | 1 – N | `dot_id` |
| 19 | `sinh_vien` | `ho_so` | 1 – N | `sinh_vien_id` |
| 20 | `giang_vien` | `ho_so` | 1 – N | `giang_vien_huong_dan_id` (có thể rỗng) |
| 21 | `de_tai` | `ho_so` | 1 – N | `de_tai_hien_tai_id` (có thể rỗng) |
| 22 | `ho_so` | `diem_dau_vao` | 1 – 1 | `ho_so_id` |
| 23 | `dot` | `lan_lay_diem` | 1 – N | `dot_id` |
| 24 | `nguoi_dung` | `lan_lay_diem` | 1 – N | `nguoi_thuc_hien_id` |
| 25 | `dot` | `ban_phan_cong` | 1 – N | `dot_id` |
| 26 | `nguoi_dung` | `ban_phan_cong` | 1 – N | `nguoi_tao_id` |
| 27 | `ban_phan_cong` | `phan_cong_huong_dan` | 1 – N | `ban_phan_cong_id` |
| 28 | `ho_so` | `phan_cong_huong_dan` | 1 – N | `ho_so_id` |
| 29 | `giang_vien` | `phan_cong_huong_dan` | 1 – N | `giang_vien_id` |
| 30 | `dot` | `de_tai_goi_y` | 1 – N | `dot_id` |
| 31 | `giang_vien` | `de_tai_goi_y` | 1 – N | `giang_vien_id` |
| 32 | `ho_so` | `de_tai` | 1 – N | `ho_so_id` |
| 33 | `de_tai_goi_y` | `de_tai` | 1 – N | `de_tai_goi_y_id` (có thể rỗng) |
| 34 | `ho_so` | `thong_tin_noi_thuc_tap` | 1 – 1 | `ho_so_id` |
| 35 | `ho_so` | `minh_chung` | 1 – N | `ho_so_id` |
| 36 | `dot_moc_thoi_gian` | `minh_chung` | 1 – N | `moc_id` (có thể rỗng) |
| 37 | `minh_chung` | `tep_dinh_kem` | 1 – N | `minh_chung_id` |
| 38 | `nguoi_dung` | `tep_dinh_kem` | 1 – N | `nguoi_tai_id` |
| 39 | `minh_chung` | `nhan_xet_minh_chung` | 1 – N | `minh_chung_id` |
| 40 | `giang_vien` | `nhan_xet_minh_chung` | 1 – N | `giang_vien_id` |
| 41 | `dot` | `hoi_dong` | 1 – N | `dot_id` |
| 42 | `hoi_dong` | `thanh_vien_hoi_dong` | 1 – N | `hoi_dong_id` |
| 43 | `giang_vien` | `thanh_vien_hoi_dong` | 1 – N | `giang_vien_id` |
| 44 | `hoi_dong` | `buoi_bao_ve` | 1 – N | `hoi_dong_id` |
| 45 | `ho_so` | `phan_cong_cham` | 1 – N | `ho_so_id` |
| 46 | `giang_vien` | `phan_cong_cham` | 1 – N | `giang_vien_id` (có thể rỗng) |
| 47 | `hoi_dong` | `phan_cong_cham` | 1 – N | `hoi_dong_id` (có thể rỗng) |
| 48 | `buoi_bao_ve` | `phan_cong_cham` | 1 – N | `buoi_bao_ve_id` (có thể rỗng) |
| 49 | `nguoi_dung` | `phan_cong_cham` | 1 – N | `nguoi_phan_cong_id` |
| 50 | `ho_so` | `diem_thanh_phan` | 1 – N | `ho_so_id` |
| 51 | `giang_vien` | `diem_thanh_phan` | 1 – N | `nguoi_cham_id` |
| 52 | `ho_so` | `xac_minh_noi_thuc_tap` | 1 – 1 | `ho_so_id` |
| 53 | `giang_vien` | `xac_minh_noi_thuc_tap` | 1 – N | `nguoi_doi_chieu_id` (có thể rỗng) |
| 54 | `ho_so` | `ket_qua_ho_so` | 1 – 1 | `ho_so_id` |
| 55 | `nguoi_dung` | `ket_qua_ho_so` | 1 – N | `nguoi_chot_id` |
| 56 | `nguoi_dung` | `thong_bao` | 1 – N | `nguoi_nhan_id` |
| 57 | `ho_so` | `thong_bao` | 1 – N | `ho_so_id` (có thể rỗng) |
| 58 | `nguoi_dung` | `nhat_ky_he_thong` | 1 – N | `nguoi_thuc_hien_id` (có thể rỗng) |


### 10.4 Ràng buộc và chỉ mục bổ sung (bắt buộc cài)

- `ho_so`: `UNIQUE(dot_id, sinh_vien_id)`.
- `phan_cong_huong_dan`: chỉ mục UNIQUE một phần trên `(ho_so_id)` **WHERE `trang_thai` NOT IN ('TU_CHOI','DA_THAY_THE')**.
- `de_tai`: chỉ mục UNIQUE một phần trên `(ho_so_id)` **WHERE `trang_thai` IN ('CHO_CHOT','DA_CHOT')**.
- `de_tai`: CHECK `nguon = 'GV_DUA_RA'` ⇒ `de_tai_goi_y_id IS NOT NULL`.
- `phan_cong_cham`: CHECK theo BR22; `buoi_bao_ve_id` (nếu có) phải thuộc đúng `hoi_dong_id`.
- `diem_thanh_phan`: `UNIQUE(ho_so_id, thanh_phan, nguoi_cham_id)`; CHECK `diem BETWEEN 0 AND 10`.
- `dot_trong_so`: `UNIQUE(dot_id, thanh_phan)`; CHECK `trong_so BETWEEN 0 AND 100`.
- `dot_moc_thoi_gian`: `UNIQUE(dot_id, ma_moc)`.
- `nguoi_dung_vai_tro`: `UNIQUE(nguoi_dung_id, vai_tro_id, khoa_id)`.
- `tai_khoan_lien_ket`: `UNIQUE(nha_cung_cap, ma_ngoai)`.
- `ho_so.giang_vien_huong_dan_id`: chỉ gán khi công bố (BR10); `ho_so.de_tai_hien_tai_id` chỉ trỏ tới `de_tai` của chính hồ sơ ở `DA_CHOT`.
- `nhat_ky_he_thong`: không cho UPDATE/DELETE (override ở model/manager, tùy chọn trigger).
- Chỉ mục truy vấn: `ho_so(dot_id, trang_thai)`, `ho_so(giang_vien_huong_dan_id)`, `thong_bao(nguoi_nhan_id, da_doc)`, `minh_chung(ho_so_id, moc_id)`.

---

## 11. Giá trị liệt kê (enum)

Lưu dạng `VARCHAR` + CHECK/`TextChoices`; **giữ đúng chuỗi**.

| Cột | Giá trị | Ý nghĩa |
|---|---|---|
| `dot.loai` | THUC_TAP, DO_AN | Loại đợt |
| `dot.trang_thai` | CHUAN_BI, PHAN_CONG, CHOT_DE_TAI, THUC_HIEN, CHAM_DIEM, HOAN_TAT | Sáu giai đoạn |
| `dot.hinh_thuc_cham` | PHAN_BIEN, HOI_DONG | HOI_DONG chỉ khi DO_AN |
| `dot_moc_thoi_gian.loai_moc` | PHAN_CONG, CHOT_DE_TAI, NOP_TIEN_DO, NOP_BAO_CAO, CHAM_DIEM | Loại mốc |
| `dot_trong_so.thanh_phan`, `diem_thanh_phan.thanh_phan` | HUONG_DAN, NOI_THUC_TAP, PHAN_BIEN, HOI_DONG | Thành phần điểm |
| `ho_so.trang_thai` | TRONG_DANH_SACH, CHO_XAC_NHAN, CHO_CHOT_DE_TAI, DANG_THUC_HIEN, CHAM_HUONG_DAN, CHO_PHAN_BIEN, HOAN_TAT | Bảy trạng thái |
| `ban_phan_cong.trang_thai` | NHAP, DA_GUI, DA_CONG_BO | Bản phân công |
| `phan_cong_huong_dan.trang_thai` | NHAP, CHO_XAC_NHAN, DONG_Y, TU_CHOI, DA_THAY_THE | Dòng phân công |
| `de_tai_goi_y.trang_thai` | MO, DONG | Đề tài gợi ý |
| `de_tai.nguon` | GV_DUA_RA, SV_DE_XUAT | Nguồn đề tài |
| `de_tai.trang_thai` | CHO_CHOT, DA_CHOT, TRA_LAI | Xử lý đề tài |
| `minh_chung.loai` | TIEN_DO, BAO_CAO_CUOI, GIAY_XAC_NHAN | Loại lần nộp |
| `minh_chung.trang_thai` | DA_NOP, CO_NHAN_XET | Trạng thái nộp |
| `diem_thanh_phan.trang_thai` | NHAP, DA_GUI | DA_GUI là khóa |
| `phan_cong_cham.loai` | PHAN_BIEN, HOI_DONG | Loại phân công chấm |
| `diem_dau_vao.nguon`, `lan_lay_diem.nguon` | USMART, FILE, KHONG_CO (chỉ `diem_dau_vao`) | Nguồn điểm TB |
| `lan_lay_diem.trang_thai` | THANH_CONG, MOT_PHAN, LOI | Kết quả lấy điểm |
| `lan_nhap_danh_sach.trang_thai` | XEM_TRUOC, DA_XAC_NHAN, HUY | Lần nhập |
| `dong_nhap_danh_sach.trang_thai_dong` | HOP_LE, TRUNG, LOI | Dòng nhập |
| `xac_minh_noi_thuc_tap.ly_do_can_xac_minh` | NGAU_NHIEN, NGHI_VAN | Lý do chọn xác minh |
| `xac_minh_noi_thuc_tap.ket_qua_xac_minh` | DA_XAC_MINH, NGHI_VAN | Kết quả xác minh |
| `nguoi_dung.loai_nguoi_dung` | SINH_VIEN, GIANG_VIEN, QUAN_TRI | Loại tài khoản |
| `nguoi_dung.trang_thai` | CHUA_KICH_HOAT, HOAT_DONG, KHOA | Tình trạng |
| `vai_tro.ma_vai_tro` | TRUONG_KHOA, GIANG_VIEN, QUAN_TRI | Vai trò hệ thống |
| `tai_khoan_lien_ket.nha_cung_cap` | USMART, GOOGLE | Nguồn danh tính |
| `tai_khoan_lien_ket.trang_thai_duyet` | TU_DONG, CHO_DUYET, DA_DUYET, TU_CHOI | Duyệt liên kết |

**Nhãn hiển thị tiếng Việt cho trạng thái hồ sơ** (dùng thống nhất mọi màn):

| Mã | Nhãn |
|---|---|
| TRONG_DANH_SACH | Chờ phân công |
| CHO_XAC_NHAN | Chờ giảng viên xác nhận |
| CHO_CHOT_DE_TAI | Đang chọn đề tài |
| DANG_THUC_HIEN | Đang thực hiện |
| CHAM_HUONG_DAN | Chờ chấm hướng dẫn |
| CHO_PHAN_BIEN | Chờ phản biện / hội đồng (hoặc "Chờ tổng hợp" nếu đợt không có phản biện/hội đồng) |
| HOAN_TAT | Hoàn tất |

---

## 12. Thông báo (trong ứng dụng)

Bảng `thong_bao`: `loai_su_kien`, `tieu_de`, `noi_dung`, `ho_so_id`, `da_doc`. Phát ra từ service khi đổi trạng thái.

| `loai_su_kien` | Người nhận | Bấm vào dẫn tới (màn) |
|---|---|---|
| PHAN_CONG_CHO_XAC_NHAN | HD | M31 |
| HD_TU_CHOI | TKhoa | M16 |
| CONG_BO_DANH_SACH | HD, SV | M30 / M50 |
| DE_TAI_CHO_CHOT | HD | M33 |
| DE_TAI_BI_TRA_LAI | SV | M51 (thấy góp ý) |
| DE_TAI_DA_CHOT | SV | M50 |
| MINH_CHUNG_MOI | HD | M35 |
| NHAN_XET_MOI | SV | M50 |
| GAN_HAN / QUA_MOC | SV (nhắc); HD, TKhoa (cờ) | M52 / M17 |
| NOP_BAO_CAO_CUOI | HD | M36 |
| DEN_LUOT_CHAM | PB, HĐ | M37 / M38 |
| NOI_THUC_TAP_NGHI_VAN | HD, TKhoa | M36 / M19 |
| SAN_SANG_PHAN_BIEN | TKhoa | M18 |
| DU_DIEM | TKhoa | M19 |
| HO_SO_HOAN_TAT | SV | M54 |
| DOI_HD | HD cũ, HD mới, SV | M30 / M50 |
| NHAC_NGUOI_CHAM | PB, HĐ, HD | màn chấm tương ứng |

---

## 13. Màn hình

Giao diện: Django Template + Bootstrap 5 + HTMX, **tiếng Việt**, sinh viên dùng nhiều trên điện thoại (responsive). Chuông thông báo cố định ở thanh trên mọi màn. Đăng nhập xong, mỗi người thấy trước **"việc đang chờ mình xử lý"** rồi mới đến menu. Chức năng giai đoạn chưa tới hiện nhưng khóa kèm lý do. Thao tác không hoàn tác (công bố, gửi điểm, chốt hồ sơ) luôn có hộp xác nhận nêu hậu quả. Bản nháp tự lưu. Làm hàng loạt, ngoại lệ làm riêng.

Mô tả hành vi chi tiết từng màn nằm trong tài liệu "Luồng chi tiết theo màn hình" của người dùng; bảng dưới là **danh mục và đường dẫn đề xuất**.

| Mã | Màn hình | Vai trò | UC | URL gợi ý |
|---|---|---|---|---|
| M01 | Đăng nhập | Tất cả | UC01 | `/dang-nhap/` |
| M02 | Chưa thuộc đợt / chờ duyệt liên kết | SV, GV | UC01 | `/chua-thuoc-dot/` |
| M03 | Thông báo | Tất cả | UC02 | `/thong-bao/` |
| M10 | Tổng quan đợt | TKhoa | — | `/khoa/` |
| M11 | Mở đợt và cấu hình | TKhoa | UC03 | `/khoa/dot/moi/`, `/khoa/dot/<id>/cau-hinh/` |
| M12 | Tải file danh sách | TKhoa | UC04 | `/khoa/dot/<id>/danh-sach/tai-len/` |
| M13 | Xem trước và xác nhận | TKhoa | UC05 | `/khoa/dot/<id>/danh-sach/xem-truoc/` |
| M14 | Lấy điểm trung bình | TKhoa | UC06 | `/khoa/dot/<id>/lay-diem/` |
| M15 | Phân công hướng dẫn (hai khung) | TKhoa | UC07, UC08 | `/khoa/dot/<id>/phan-cong/` |
| M16 | Theo dõi xác nhận và công bố | TKhoa | UC09 | `/khoa/dot/<id>/phan-cong/theo-doi/` |
| M17 | Theo dõi tiến độ | TKhoa | UC18 | `/khoa/dot/<id>/tien-do/` |
| M18 | Phân công phản biện/hội đồng | TKhoa | UC22 | `/khoa/dot/<id>/cham-diem/phan-cong/` |
| M19 | Tổng hợp điểm và lưu hồ sơ | TKhoa | UC25, UC26 | `/khoa/dot/<id>/tong-hop/` |
| M20 | Hồ sơ đã lưu | TKhoa | UC25 | `/khoa/ho-so-da-luu/` |
| M30 | Việc của tôi | Giảng viên | — | `/giang-vien/` |
| M31 | Xác nhận phân công | HD | UC10 | `/giang-vien/xac-nhan-phan-cong/` |
| M32 | Đề tài của tôi | HD | UC12 | `/giang-vien/de-tai/` |
| M33 | Chốt đề tài | HD | UC15 | `/giang-vien/chot-de-tai/` |
| M34 | Sinh viên của tôi | HD | — | `/giang-vien/sinh-vien/` |
| M35 | Chi tiết sinh viên, nhận xét minh chứng | HD | UC17 | `/giang-vien/sinh-vien/<ho_so_id>/` |
| M36 | Chấm hướng dẫn (chia đôi) | HD | UC20, UC31, UC21 | `/giang-vien/cham/huong-dan/<ho_so_id>/` |
| M37 | Chấm phản biện | PB | UC23 | `/giang-vien/cham/phan-bien/<ho_so_id>/` |
| M38 | Chấm hội đồng (buổi → sinh viên → chấm) | HĐ | UC24 | `/giang-vien/hoi-dong/` |
| M50 | Hồ sơ của tôi | SV | UC11 | `/sinh-vien/` |
| M51 | Chọn hoặc đề xuất đề tài | SV | UC13, UC14 | `/sinh-vien/de-tai/` |
| M52 | Nộp minh chứng | SV | UC16 | `/sinh-vien/minh-chung/<moc_id>/` |
| M53 | Nộp báo cáo cuối | SV | UC19 | `/sinh-vien/bao-cao-cuoi/` |
| M54 | Xem kết quả | SV | UC27 | `/sinh-vien/ket-qua/` |
| M60 | Tài khoản và phân quyền | QT | UC28 | `/quan-tri/tai-khoan/` |
| M61 | Khoa và bộ môn | QT | UC29 | `/quan-tri/khoa-bo-mon/` |
| M62 | Nhật ký hệ thống | QT | UC30 | `/quan-tri/nhat-ky/` |

**Màn M50 "Hồ sơ của tôi" luôn có đúng một ô "Việc tiếp theo của bạn"**, đổi theo trạng thái:

| Trạng thái hồ sơ | Việc tiếp theo hiển thị |
|---|---|
| TRONG_DANH_SACH, CHO_XAC_NHAN | "Chưa có giảng viên hướng dẫn. Bạn sẽ được thông báo khi khoa công bố." (không có nút) |
| CHO_CHOT_DE_TAI (chưa gửi đề tài) | Nút "Chọn hoặc đề xuất đề tài" |
| CHO_CHOT_DE_TAI (đã gửi) | "Chờ giảng viên chốt" |
| CHO_CHOT_DE_TAI (bị trả lại) | "Sửa và gửi lại đề tài" + góp ý |
| DANG_THUC_HIEN | Nút "Nộp minh chứng" cho mốc đang mở; hết mốc tiến độ và đến hạn thì "Nộp báo cáo cuối" |
| CHAM_HUONG_DAN, CHO_PHAN_BIEN | "Đang chờ chấm điểm" (không có nút) |
| HOAN_TAT | "Xem kết quả" |

Sơ đồ chuyển màn chính: TKhoa M01→M10→M11→M12→M13→M14→M15→M16→M17→M18→M19→M20. Giảng viên M01→M30→M31→M32→M33→M34→M35→M36 (PB: M30→M37; HĐ: M30→M38). Sinh viên M01→M50→M51→M52→M53→M54 (mọi bước quay về M50). Quản trị M01→M60/M61/M62.

---

## 14. Cấu trúc dự án Django đề xuất

```
project/
├── manage.py
├── config/                 # settings (base/dev/prod), urls, wsgi
├── core/                   # state.py (transition), permissions, mixins, errors, audit helper, constants/enums
├── accounts/               # nguoi_dung, tai_khoan_lien_ket, vai_tro, nguoi_dung_vai_tro; auth backend; đăng nhập
├── organization/           # khoa, bo_mon, sinh_vien, giang_vien
├── dots/                   # dot, dot_moc_thoi_gian, dot_trong_so
├── hoso/                   # ho_so, diem_dau_vao, lan_lay_diem, lan_nhap_danh_sach, dong_nhap_danh_sach (nhập Excel)
├── phancong/               # ban_phan_cong, phan_cong_huong_dan, thuật toán gợi ý chia đều
├── detai/                  # de_tai_goi_y, de_tai
├── thuchien/               # thong_tin_noi_thuc_tap, minh_chung, tep_dinh_kem, nhan_xet_minh_chung
├── chamdiem/               # hoi_dong, thanh_vien_hoi_dong, buoi_bao_ve, phan_cong_cham, diem_thanh_phan, xac_minh_noi_thuc_tap, ket_qua_ho_so, tính điểm
├── hethong/                # thong_bao, nhat_ky_he_thong
├── integrations/usmart/    # base.py (Protocol), mock.py, real.py
├── templates/              # base.html, components/, từng app
├── static/
├── fixtures/               # dữ liệu mẫu (mục 18), usmart_gpa.json
├── docker/                 # Dockerfile, nginx.conf
├── docker-compose.yml
├── .env.example
└── tests/
```

Tên app là **đề xuất**; giữ nhất quán một khi đã chọn.

---

## 15. Bảo mật, tệp và nhật ký

- Xác thực qua `UsmartClient` (mục 9); phiên Django; `SESSION_COOKIE_SECURE`, CSRF bật, `SECURE_*` ở production.
- Mọi view kiểm tra quyền + phạm vi (mục 4.2). **Test bắt buộc:** thử truy cập chéo (khoa khác, hồ sơ người khác, sinh viên vào màn giảng viên) phải bị từ chối.
- Tệp: whitelist phần mở rộng (mặc định `pdf, doc, docx, xls, xlsx, ppt, pptx, zip, rar, png, jpg, jpeg`), giới hạn dung lượng (mặc định 20 MB, cấu hình), đổi tên tệp lưu bằng UUID, lưu ngoài thư mục tĩnh, tải về qua view kiểm tra quyền.
- Nhật ký: ghi `nguoi_thuc_hien_id`, `hanh_dong`, `doi_tuong_loai`, `doi_tuong_id`, `mo_ta`, `dia_chi_ip`; không ghi điểm; không sửa/xóa.
- Không đưa mật khẩu, khóa API vào mã nguồn; dùng biến môi trường.
- Chống lạm dụng: giới hạn lần thử lấy điểm; chống tải trùng file danh sách (cảnh báo).

---

## 16. Cấu hình và triển khai

Biến môi trường (`.env.example`): `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`, `USMART_MODE` (`mock`|`real`), `USMART_BASE_URL`, `USMART_CLIENT_ID`, `USMART_CLIENT_SECRET`, `MEDIA_ROOT`, `MAX_UPLOAD_MB`, `XAC_MINH_TY_LE`, `SO_LAM_TRON_DIEM`, `GOOGLE_LOGIN_ENABLED`.

Docker Compose: dịch vụ `web` (Gunicorn), `db` (PostgreSQL, volume), `nginx` (tĩnh + proxy); volume cho `media`. Migrate chạy khi khởi động. **Triển khai thật chỉ sau khi thầy duyệt** (demo trên host miễn phí; dữ liệu thật trên máy chủ/tên miền phụ của trường).

---

## 17. Kế hoạch triển khai và tiêu chí hoàn thành

### 17.1 Thứ tự làm đề xuất (backend + giao diện đi cùng)

0. Khung dự án: Docker Compose, settings, `base.html` Bootstrap 5 + HTMX, `core` (enums, lỗi, `transition_ho_so`), `.env.example`.
1. `accounts` + `organization` + `integrations/usmart` (mock) + đăng nhập + phân quyền + selector theo phạm vi + dữ liệu mẫu. (UC01, UC28, UC29, UC30 khung, UC02 khung)
2. `dots`: mở đợt, mốc, trọng số. (UC03)
3. `hoso`: tải Excel, xem trước, xác nhận, tạo hồ sơ; lấy điểm. (UC04, UC05, UC06)
4. `phancong`: màn hai khung, gợi ý chia đều, gửi, xác nhận/từ chối, công bố, đổi HD. (UC07–UC11)
5. `detai`: đưa ra/chọn/đề xuất/chốt. (UC12–UC15)
6. `thuchien`: minh chứng, nhận xét, theo dõi tiến độ, nhắc. (UC16–UC18)
7. `chamdiem`: nộp báo cáo cuối, chấm hướng dẫn + nơi thực tập + xác minh. (UC19–UC21, UC31)
8. `chamdiem`: phân công phản biện/hội đồng, chấm PB/HĐ. (UC22–UC24)
9. Tổng hợp và lưu hồ sơ, xem kết quả. (UC25–UC27)
10. Thông báo đầy đủ, nhật ký, hoàn thiện, kiểm tra quyền toàn hệ thống.

Nếu người dùng đã có sprint giao diện riêng, **theo sprint của người dùng** nhưng không phá thứ tự phụ thuộc (ví dụ phân công cần có đợt và hồ sơ).

### 17.2 Definition of Done cho mỗi use case

- Chạy được từ giao diện bằng dữ liệu mẫu, đủ luồng chính và các nhánh lỗi ghi ở mục 6 và 7.
- Mọi chuyển trạng thái đi qua `transition_ho_so`/hàm đợt tương ứng; có ghi nhật ký và phát thông báo.
- Kiểm tra quyền + phạm vi; có test truy cập trái phép.
- Giao diện tiếng Việt, dùng được trên điện thoại (màn sinh viên).
- Migration sạch, không cảnh báo; không lệch tên bảng/cột/enum.

### 17.3 Test bắt buộc

1. Thuật toán gợi ý chia đều (8.1): chênh số lượng ≤ 1, cân bằng điểm, hạn mức, nhóm chưa có điểm, hết chỗ.
2. Tính điểm cuối (8.2): đủ/thiếu thành phần, hội đồng trung bình, trọng số ≠ 100 bị chặn, ảnh chụp trọng số.
3. Máy trạng thái hồ sơ: mọi chuyển hợp lệ và mọi chuyển **bị cấm**; nhánh HD từ chối.
4. Phân quyền: truy cập chéo khoa/hồ sơ, sinh viên không sửa điểm, PB ≠ HD, điểm TB chỉ TKhoa.
5. Nhập Excel: dòng lỗi/trùng/khác khoa, xác nhận một transaction.
6. Ràng buộc DB: chỉ mục UNIQUE một phần (BR11, BR12), CHECK (BR17, BR22).
7. Xác minh nơi thực tập: bắt buộc đối chiếu bản gốc, kết quả xác minh trước khi gửi điểm.

---

## 18. Dữ liệu mẫu (fixture để phát triển và demo)

- 1 khoa: "Khoa Công nghệ thông tin" (và 1 khoa khác để thử cách ly dữ liệu), 2 bộ môn.
- Tài khoản: 1 quản trị, 1 trưởng khoa (khoa CNTT), 8 giảng viên (4 người vừa là HD vừa là PB), 40 sinh viên.
- Điểm mẫu `usmart_gpa.json`: 40 sinh viên, điểm hệ 4 từ 1.8 đến 3.9, **5 sinh viên không có điểm**.
- 1 đợt "Thực tập tốt nghiệp HK1 2026-2027", `so_sv_toi_da_moi_gv = 8`, trọng số mẫu HUONG_DAN 50 / NOI_THUC_TAP 30 / PHAN_BIEN 20 (**số mẫu, chưa phải quy định**), mốc: xác nhận phân công, chốt đề tài, 3 mốc nộp tiến độ, nộp báo cáo cuối.
- 1 file Excel danh sách mẫu (có vài dòng lỗi, trùng) để thử UC04–UC05.
- Tên mẫu: TS. Nguyễn Văn An, ThS. Trần Thị Bình, ThS. Lê Quốc Cường, TS. Phạm Minh Đức; sinh viên Nguyễn Khánh Duy (22A1234)…

---

## 19. Giả định và điểm chưa chốt (agent dùng mặc định, ghi `# ASSUMPTION`)

| # | Điểm | Mặc định dùng ngay | Cần ai xác nhận |
|---|---|---|---|
| 1 | Tích hợp USMART (SSO + đọc điểm) | Mock; adapter sẵn; dự phòng Google + điểm trong file | Thầy và nhà trường |
| 2 | Điểm TB hệ 4 hay hệ 10 | Hệ 4 tích lũy | — |
| 3 | Ai mở đợt, tải danh sách | Trưởng khoa (quyền tách riêng, gán lại được sau) | Thầy |
| 4 | Thang điểm, trọng số thực tế | Thang 10; trọng số cấu hình theo đợt; số mẫu 50/30/20 | **Thầy (bắt buộc)** |
| 5 | Điểm hội đồng | Mỗi thành viên chấm riêng, lấy trung bình | Thầy (nên hỏi) |
| 6 | Thực tập có phản biện không | Cấu hình `hinh_thuc_cham`; mặc định theo luồng thầy kể: có phản biện | **Thầy** |
| 7 | Đổi HD sau công bố | Cho TKhoa đổi, bắt buộc lý do, giữ lịch sử `DA_THAY_THE` (chưa có trong 31 UC, báo thầy) | Thầy |
| 8 | Hội đồng nhiều buổi | Có bảng `buoi_bao_ve` | Thầy (nên hỏi) |
| 9 | Chuyển giai đoạn đợt | Tự động ở CHUAN_BI→PHAN_CONG, PHAN_CONG→CHOT_DE_TAI, →HOAN_TAT; còn lại thủ công | Thầy |
| 10 | Tỷ lệ xác minh ngẫu nhiên nơi thực tập | `XAC_MINH_TY_LE = 0.10` | Thầy |
| 11 | Quy tắc làm tròn điểm cuối | 2 chữ số thập phân | Thầy |
| 12 | Đợt không có phản biện/hội đồng | Bỏ UC22; hồ sơ "Chờ tổng hợp" | Thầy |
| 13 | Thông báo | Chỉ trong ứng dụng, không email | — |
| 14 | PB có thấy điểm HD/nơi thực tập trước khi chấm | Không (chấm độc lập) | Thầy |
| 15 | Phản hồi phân công | Từ chối là từ chối cả bản gửi; gửi lại chỉ các dòng NHAP mới | — |

---

## 20. Thuật ngữ

| Thuật ngữ | Nghĩa |
|---|---|
| Đợt | Một đợt thực tập hoặc đồ án của một khoa trong một học kỳ |
| Hồ sơ (`ho_so`) | Bản ghi theo dõi một sinh viên trong một đợt, xuyên suốt vòng đời |
| GVHD / HD | Giảng viên hướng dẫn |
| PB | Giảng viên phản biện |
| HĐ | Thành viên hội đồng chấm đồ án |
| TKhoa | Trưởng khoa |
| QT | Quản trị hệ thống |
| Minh chứng | Tệp sinh viên nộp theo mốc để chứng minh tiến độ |
| Nơi thực tập | Đơn vị bên ngoài tiếp nhận sinh viên thực tập; không có tài khoản |
| USMART | Cổng thông tin sinh viên của Đại học Vinh (nguồn đăng nhập và điểm TB) |
| Điểm TB | Điểm trung bình tích lũy hệ 4 (kèm tín chỉ tích lũy) |
| Bản nháp phân công | Bản phân công chưa gửi/chưa công bố, sửa tự do |
| Công bố | Hành động không hoàn tác chuyển bản phân công thành chính thức |
