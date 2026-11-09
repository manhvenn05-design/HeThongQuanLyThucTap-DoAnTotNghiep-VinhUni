**THIẾT KẾ CƠ SỞ DỮ LIỆU**

**Hệ thống quản lý điều phối thực tập và đồ án tốt nghiệp – Trường Kỹ thuật và Công nghệ, Đại học Vinh**

*Phiên bản 0.1 (bản nháp để thầy xem) – khớp bộ 31 use case UC01–UC31. CSDL: PostgreSQL; ứng dụng: Django.*
# **1. Tổng quan và nguyên tắc thiết kế**
- Gồm 32 bảng chia 8 nhóm (A–H). Mỗi bảng có khóa chính id BIGINT tự tăng; tên bảng, cột viết tiếng Việt không dấu, dạng snake\_case.
- Bảng ho\_so là trung tâm: mỗi sinh viên trong mỗi đợt có đúng một hồ sơ; trạng thái hồ sơ lưu 7 giá trị theo vòng đời đã thống nhất.
- Tách vai trò khỏi người: HD, PB, HĐ không phải ba loại tài khoản mà là ba vai của cùng một giảng viên, xác định theo từng hồ sơ (phân công hướng dẫn, phan\_cong\_cham).
- Dữ liệu theo khoa: đợt, hồ sơ, vai trò đều gắn khoa\_id; truy vấn của TKhoa luôn lọc theo khoa của mình.
- Điểm đầu vào (điểm TB tích lũy) nằm ở bảng riêng diem\_dau\_vao để chỉ TKhoa được xem; sinh viên và giảng viên không đọc được.
- Không lưu mật khẩu cổng USMART. Đăng nhập qua tài khoản liên kết (tai\_khoan\_lien\_ket); nếu chưa tích hợp được thì dùng Google và TKhoa duyệt liên kết mã sinh viên.
- Điểm thành phần và điểm cuối tách bảng; điểm cuối lưu kèm ảnh chụp trọng số tại thời điểm chốt để đổi cấu hình sau này không làm lệch kết quả cũ.
- Nhật ký chỉ thêm, không sửa, không ghi giá trị điểm. Tệp lưu ngoài CSDL (đĩa hoặc object storage), CSDL chỉ giữ đường dẫn.
# **2. Danh sách bảng**

|**STT**|**Tên bảng**|**Nhóm**|**Mục đích**|**Use case**|
| :- | :- | :- | :- | :- |
|1|**khoa**|A. Tổ chức và người dùng|Danh mục khoa của trường (phạm vi dữ liệu theo khoa)|UC29|
|2|**bo\_mon**|A. Tổ chức và người dùng|Danh mục bộ môn thuộc khoa|UC29|
|3|**nguoi\_dung**|A. Tổ chức và người dùng|Tài khoản dùng chung cho mọi người dùng; không lưu mật khẩu cổng|UC01, UC28|
|4|**tai\_khoan\_lien\_ket**|A. Tổ chức và người dùng|Liên kết tài khoản hệ thống với danh tính ở bên ngoài (USMART, Google)|UC01|
|5|**sinh\_vien**|A. Tổ chức và người dùng|Thông tin riêng của sinh viên; được tạo khi nhập danh sách, trước lần đăng nhập đầu|UC01, UC04, UC05|
|6|**giang\_vien**|A. Tổ chức và người dùng|Thông tin riêng của giảng viên (dùng chung cho vai trò HD, PB, HĐ)|UC10, UC22|
|7|**vai\_tro**|A. Tổ chức và người dùng|Danh mục vai trò hệ thống|UC28|
|8|**nguoi\_dung\_vai\_tro**|A. Tổ chức và người dùng|Gán vai trò cho người dùng, giới hạn theo khoa|UC28|
|9|**dot**|B. Đợt và cấu hình|Một đợt thực tập hoặc đồ án tốt nghiệp của một khoa|UC03|
|10|**dot\_moc\_thoi\_gian**|B. Đợt và cấu hình|Các mốc thời gian của đợt (nộp minh chứng, nộp báo cáo, chấm điểm…)|UC03, UC16, UC18|
|11|**dot\_trong\_so**|B. Đợt và cấu hình|Trọng số các thành phần điểm của đợt|UC03, UC26|
|12|**lan\_nhap\_danh\_sach**|C. Danh sách và điểm đầu vào|Mỗi lần tải file danh sách của Phòng đào tạo lên hệ thống|UC04, UC05|
|13|**dong\_nhap\_danh\_sach**|C. Danh sách và điểm đầu vào|Từng dòng bóc tách từ file, dùng cho bước xem trước và xác nhận|UC05|
|14|**ho\_so**|C. Danh sách và điểm đầu vào|Hồ sơ của một sinh viên trong một đợt; bảng trung tâm theo dõi vòng đời|UC05–UC27|
|15|**diem\_dau\_vao**|C. Danh sách và điểm đầu vào|Điểm TB tích lũy dùng để gợi ý chia đều; tách bảng để chỉ TKhoa được xem|UC06, UC08|
|16|**lan\_lay\_diem**|C. Danh sách và điểm đầu vào|Nhật ký mỗi lần lấy điểm TB từ USMART (một lần khi chốt danh sách)|UC06|
|17|**ban\_phan\_cong**|D. Phân công hướng dẫn|Bản phân công hướng dẫn của một đợt (nháp → gửi → công bố)|UC07, UC09|
|18|**phan\_cong\_huong\_dan**|D. Phân công hướng dẫn|Từng dòng phân công một hồ sơ cho một giảng viên và phản hồi của HD|UC07, UC08, UC10, UC11|
|19|**de\_tai\_goi\_y**|E. Đề tài|Đề tài do giảng viên đưa ra để sinh viên chọn|UC12, UC13|
|20|**de\_tai**|E. Đề tài|Đề tài của một hồ sơ (chọn từ gợi ý hoặc sinh viên đề xuất) và kết quả chốt|UC13, UC14, UC15|
|21|**thong\_tin\_noi\_thuc\_tap**|F. Thực hiện và minh chứng|Thông tin liên hệ nơi thực tập, dùng để xác minh điểm nơi thực tập|UC16, UC31|
|22|**minh\_chung**|F. Thực hiện và minh chứng|Mỗi lần sinh viên nộp minh chứng tiến độ, báo cáo cuối hoặc giấy xác nhận|UC16, UC17, UC19|
|23|**tep\_dinh\_kem**|F. Thực hiện và minh chứng|Tệp thuộc một lần nộp minh chứng (báo cáo, sản phẩm, bản scan giấy xác nhận)|UC16, UC19|
|24|**nhan\_xet\_minh\_chung**|F. Thực hiện và minh chứng|Nhận xét của HD cho từng lần nộp|UC17|
|25|**hoi\_dong**|G. Chấm điểm và kết quả|Hội đồng chấm đồ án tốt nghiệp|UC22, UC24|
|26|**thanh\_vien\_hoi\_dong**|G. Chấm điểm và kết quả|Giảng viên là thành viên của hội đồng|UC22, UC24|
|27|**phan\_cong\_cham**|G. Chấm điểm và kết quả|Phân công phản biện hoặc hội đồng cho từng hồ sơ|UC22|
|28|**diem\_thanh\_phan**|G. Chấm điểm và kết quả|Điểm của từng thành phần do người chấm nhập|UC20, UC21, UC23, UC24|
|29|**xac\_minh\_noi\_thuc\_tap**|G. Chấm điểm và kết quả|Đối chiếu bản gốc và xác minh điểm nơi thực tập (chống giả mạo)|UC20, UC31|
|30|**ket\_qua\_ho\_so**|G. Chấm điểm và kết quả|Điểm cuối và việc lưu hồ sơ|UC25, UC26, UC27|
|31|**thong\_bao**|H. Hệ thống|Thông báo gửi đến người dùng|UC02|
|32|**nhat\_ky\_he\_thong**|H. Hệ thống|Nhật ký hành động quan trọng; chỉ thêm, không sửa; không ghi nội dung điểm|UC30|
# **3. Chi tiết từng bảng**
## **Nhóm A. Tổ chức và người dùng**
### **1. khoa**
*Danh mục khoa của trường (phạm vi dữ liệu theo khoa) (UC: UC29)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**ma\_khoa**|VARCHAR(20)|NOT NULL, UNIQUE|Mã khoa|
|**ten\_khoa**|VARCHAR(200)|NOT NULL|Tên khoa|
|**dang\_hoat\_dong**|BOOLEAN|NOT NULL, mặc định TRUE|Còn sử dụng hay không|

### **2. bo\_mon**
*Danh mục bộ môn thuộc khoa (UC: UC29)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**khoa\_id**|BIGINT|FK → khoa.id, NOT NULL|Khoa chủ quản|
|**ma\_bo\_mon**|VARCHAR(20)|NOT NULL, UNIQUE(khoa\_id, ma\_bo\_mon)|Mã bộ môn|
|**ten\_bo\_mon**|VARCHAR(200)|NOT NULL|Tên bộ môn|
|**dang\_hoat\_dong**|BOOLEAN|NOT NULL, mặc định TRUE|Còn sử dụng hay không|

### **3. nguoi\_dung**
*Tài khoản dùng chung cho mọi người dùng; không lưu mật khẩu cổng (UC: UC01, UC28)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**ma\_dinh\_danh\_cong**|VARCHAR(50)|NOT NULL, UNIQUE|Mã đăng nhập trên cổng (USMART): mã sinh viên hoặc mã cán bộ|
|**ho\_ten**|VARCHAR(150)|NOT NULL|Họ và tên|
|**email**|VARCHAR(150)|UNIQUE, NULL|Email liên hệ|
|**so\_dien\_thoai**|VARCHAR(20)|NULL|Số điện thoại|
|**loai\_nguoi\_dung**|VARCHAR(20)|NOT NULL, CHECK|SINH\_VIEN / GIANG\_VIEN / QUAN\_TRI|
|**trang\_thai**|VARCHAR(20)|NOT NULL, CHECK|CHUA\_KICH\_HOAT / HOAT\_DONG / KHOA|
|**lan\_dang\_nhap\_cuoi**|TIMESTAMPTZ|NULL|Lần đăng nhập gần nhất|
|**ngay\_tao**|TIMESTAMPTZ|NOT NULL, mặc định now()|Ngày tạo|

### **4. tai\_khoan\_lien\_ket**
*Liên kết tài khoản hệ thống với danh tính ở bên ngoài (USMART, Google) (UC: UC01)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**nguoi\_dung\_id**|BIGINT|FK → nguoi\_dung.id, NOT NULL|Người dùng|
|**nha\_cung\_cap**|VARCHAR(20)|NOT NULL, CHECK|USMART / GOOGLE|
|**ma\_ngoai**|VARCHAR(100)|NOT NULL, UNIQUE(nha\_cung\_cap, ma\_ngoai)|Mã định danh phía nhà cung cấp|
|**email**|VARCHAR(150)|NULL|Email phía nhà cung cấp|
|**trang\_thai\_duyet**|VARCHAR(20)|NOT NULL, CHECK|TU\_DONG / CHO\_DUYET / DA\_DUYET / TU\_CHOI (phương án dự phòng Google do TKhoa duyệt liên kết MSSV)|
|**ngay\_lien\_ket**|TIMESTAMPTZ|NOT NULL|Ngày liên kết|

### **5. sinh\_vien**
*Thông tin riêng của sinh viên; được tạo khi nhập danh sách, trước lần đăng nhập đầu (UC: UC01, UC04, UC05)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**nguoi\_dung\_id**|BIGINT|FK → nguoi\_dung.id, UNIQUE, NOT NULL|Tài khoản tương ứng|
|**ma\_sinh\_vien**|VARCHAR(20)|NOT NULL, UNIQUE|Mã sinh viên|
|**lop**|VARCHAR(50)|NULL|Lớp sinh hoạt|
|**khoa\_id**|BIGINT|FK → khoa.id, NOT NULL|Khoa của sinh viên|

### **6. giang\_vien**
*Thông tin riêng của giảng viên (dùng chung cho vai trò HD, PB, HĐ) (UC: UC10, UC22)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**nguoi\_dung\_id**|BIGINT|FK → nguoi\_dung.id, UNIQUE, NOT NULL|Tài khoản tương ứng|
|**ma\_can\_bo**|VARCHAR(20)|NOT NULL, UNIQUE|Mã cán bộ|
|**khoa\_id**|BIGINT|FK → khoa.id, NOT NULL|Khoa công tác|
|**bo\_mon\_id**|BIGINT|FK → bo\_mon.id, NULL|Bộ môn|
|**hoc\_vi**|VARCHAR(50)|NULL|Học vị, học hàm|

### **7. vai\_tro**
*Danh mục vai trò hệ thống (UC: UC28)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**ma\_vai\_tro**|VARCHAR(20)|NOT NULL, UNIQUE|TRUONG\_KHOA / GIANG\_VIEN / QUAN\_TRI (SV xác định qua bảng sinh\_vien)|
|**ten\_vai\_tro**|VARCHAR(100)|NOT NULL|Tên hiển thị|
|**mo\_ta**|VARCHAR(300)|NULL|Mô tả|

### **8. nguoi\_dung\_vai\_tro**
*Gán vai trò cho người dùng, giới hạn theo khoa (UC: UC28)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**nguoi\_dung\_id**|BIGINT|FK → nguoi\_dung.id, NOT NULL|Người dùng|
|**vai\_tro\_id**|BIGINT|FK → vai\_tro.id, NOT NULL|Vai trò|
|**khoa\_id**|BIGINT|FK → khoa.id, NULL|Phạm vi khoa (NULL với quản trị)|
|**hieu\_luc\_tu**|DATE|NOT NULL|Ngày bắt đầu hiệu lực|
|**hieu\_luc\_den**|DATE|NULL|Ngày hết hiệu lực; UNIQUE(nguoi\_dung\_id, vai\_tro\_id, khoa\_id)|

## **Nhóm B. Đợt và cấu hình**
### **9. dot**
*Một đợt thực tập hoặc đồ án tốt nghiệp của một khoa (UC: UC03)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**ma\_dot**|VARCHAR(30)|NOT NULL, UNIQUE|Mã đợt|
|**ten\_dot**|VARCHAR(200)|NOT NULL|Tên đợt|
|**loai**|VARCHAR(20)|NOT NULL, CHECK|THUC\_TAP / DO\_AN|
|**hoc\_ky**|SMALLINT|NOT NULL, CHECK 1..3|Học kỳ|
|**nam\_hoc**|VARCHAR(9)|NOT NULL|Ví dụ 2026-2027|
|**khoa\_id**|BIGINT|FK → khoa.id, NOT NULL|Khoa sở hữu đợt|
|**trang\_thai**|VARCHAR(20)|NOT NULL, CHECK|CHUAN\_BI / PHAN\_CONG / CHOT\_DE\_TAI / THUC\_HIEN / CHAM\_DIEM / HOAN\_TAT|
|**so\_sv\_toi\_da\_moi\_gv**|SMALLINT|NOT NULL, CHECK > 0|Hạn mức sinh viên tối đa cho mỗi giảng viên hướng dẫn|
|**hinh\_thuc\_cham**|VARCHAR(20)|NOT NULL, CHECK|PHAN\_BIEN / HOI\_DONG (HOI\_DONG chỉ cho đồ án)|
|**nguoi\_tao\_id**|BIGINT|FK → nguoi\_dung.id, NOT NULL|Người mở đợt|
|**ngay\_tao**|TIMESTAMPTZ|NOT NULL, mặc định now()|Ngày tạo|

### **10. dot\_moc\_thoi\_gian**
*Các mốc thời gian của đợt (nộp minh chứng, nộp báo cáo, chấm điểm…) (UC: UC03, UC16, UC18)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**dot\_id**|BIGINT|FK → dot.id, NOT NULL|Đợt|
|**ma\_moc**|VARCHAR(30)|NOT NULL, UNIQUE(dot\_id, ma\_moc)|Mã mốc|
|**ten\_moc**|VARCHAR(150)|NOT NULL|Tên mốc|
|**loai\_moc**|VARCHAR(20)|NOT NULL, CHECK|PHAN\_CONG / CHOT\_DE\_TAI / NOP\_TIEN\_DO / NOP\_BAO\_CAO / CHAM\_DIEM|
|**thu\_tu**|SMALLINT|NOT NULL|Thứ tự trong đợt|
|**han\_cuoi**|TIMESTAMPTZ|NOT NULL|Hạn cuối của mốc|

### **11. dot\_trong\_so**
*Trọng số các thành phần điểm của đợt (UC: UC03, UC26)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**dot\_id**|BIGINT|FK → dot.id, NOT NULL|Đợt|
|**thanh\_phan**|VARCHAR(20)|NOT NULL, CHECK, UNIQUE(dot\_id, thanh\_phan)|HUONG\_DAN / NOI\_THUC\_TAP / PHAN\_BIEN / HOI\_DONG|
|**trong\_so**|NUMERIC(5,2)|NOT NULL, CHECK 0..100|Trọng số (%); tổng các dòng của đợt = 100 (kiểm tra ở tầng ứng dụng khi lưu cấu hình)|

## **Nhóm C. Danh sách và điểm đầu vào**
### **12. lan\_nhap\_danh\_sach**
*Mỗi lần tải file danh sách của Phòng đào tạo lên hệ thống (UC: UC04, UC05)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**dot\_id**|BIGINT|FK → dot.id, NOT NULL|Đợt|
|**nguoi\_tai\_id**|BIGINT|FK → nguoi\_dung.id, NOT NULL|Người tải file (TKhoa)|
|**ten\_tep**|VARCHAR(255)|NOT NULL|Tên file gốc|
|**duong\_dan**|VARCHAR(500)|NOT NULL|Đường dẫn lưu file|
|**tong\_dong**|INTEGER|NOT NULL, mặc định 0|Tổng số dòng đọc được|
|**dong\_hop\_le**|INTEGER|NOT NULL, mặc định 0|Số dòng hợp lệ|
|**dong\_loi**|INTEGER|NOT NULL, mặc định 0|Số dòng lỗi|
|**trang\_thai**|VARCHAR(20)|NOT NULL, CHECK|XEM\_TRUOC / DA\_XAC\_NHAN / HUY|
|**ngay\_tai**|TIMESTAMPTZ|NOT NULL, mặc định now()|Ngày tải|

### **13. dong\_nhap\_danh\_sach**
*Từng dòng bóc tách từ file, dùng cho bước xem trước và xác nhận (UC: UC05)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**lan\_nhap\_id**|BIGINT|FK → lan\_nhap\_danh\_sach.id, NOT NULL|Lần nhập|
|**so\_dong**|INTEGER|NOT NULL|Số thứ tự dòng trong file|
|**ma\_sinh\_vien**|VARCHAR(20)|NOT NULL|Mã sinh viên đọc được|
|**ho\_ten**|VARCHAR(150)|NULL|Họ tên|
|**lop**|VARCHAR(50)|NULL|Lớp|
|**diem\_tb**|NUMERIC(4,2)|NULL|Điểm trong file (chỉ dùng cho phương án dự phòng)|
|**trang\_thai\_dong**|VARCHAR(20)|NOT NULL, CHECK|HOP\_LE / TRUNG / LOI|
|**loi**|VARCHAR(300)|NULL|Mô tả lỗi (sai mã, trùng, khác khoa…)|

### **14. ho\_so**
*Hồ sơ của một sinh viên trong một đợt; bảng trung tâm theo dõi vòng đời (UC: UC05–UC27)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**dot\_id**|BIGINT|FK → dot.id, NOT NULL|Đợt|
|**sinh\_vien\_id**|BIGINT|FK → sinh\_vien.id, NOT NULL|Sinh viên; UNIQUE(dot\_id, sinh\_vien\_id)|
|**trang\_thai**|VARCHAR(25)|NOT NULL, CHECK|TRONG\_DANH\_SACH / CHO\_XAC\_NHAN / CHO\_CHOT\_DE\_TAI / DANG\_THUC\_HIEN / CHAM\_HUONG\_DAN / CHO\_PHAN\_BIEN / HOAN\_TAT|
|**giang\_vien\_huong\_dan\_id**|BIGINT|FK → giang\_vien.id, NULL|HD hiện tại (chỉ có sau khi HD đồng ý)|
|**de\_tai\_hien\_tai\_id**|BIGINT|FK → de\_tai.id, NULL|Đề tài đã chốt|
|**ngay\_tao**|TIMESTAMPTZ|NOT NULL, mặc định now()|Ngày tạo|
|**ngay\_cap\_nhat**|TIMESTAMPTZ|NOT NULL|Lần đổi trạng thái gần nhất|

### **15. diem\_dau\_vao**
*Điểm TB tích lũy dùng để gợi ý chia đều; tách bảng để chỉ TKhoa được xem (UC: UC06, UC08)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**ho\_so\_id**|BIGINT|FK → ho\_so.id, UNIQUE, NOT NULL|Hồ sơ|
|**diem\_tb\_he4**|NUMERIC(3,2)|NULL, CHECK 0..4|Điểm TB tích lũy hệ 4|
|**tin\_chi\_tich\_luy**|SMALLINT|NULL|Số tín chỉ tích lũy|
|**ngay\_lay**|TIMESTAMPTZ|NULL|Ngày lấy điểm|
|**nguon**|VARCHAR(20)|NOT NULL, CHECK|USMART / FILE / KHONG\_CO (KHONG\_CO → nhóm chưa có điểm)|

### **16. lan\_lay\_diem**
*Nhật ký mỗi lần lấy điểm TB từ USMART (một lần khi chốt danh sách) (UC: UC06)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**dot\_id**|BIGINT|FK → dot.id, NOT NULL|Đợt|
|**nguoi\_thuc\_hien\_id**|BIGINT|FK → nguoi\_dung.id, NOT NULL|Người thực hiện|
|**nguon**|VARCHAR(20)|NOT NULL, CHECK|USMART / FILE|
|**ngay\_lay**|TIMESTAMPTZ|NOT NULL, mặc định now()|Thời điểm lấy|
|**so\_sv\_co\_diem**|INTEGER|NOT NULL|Số SV lấy được điểm|
|**so\_sv\_thieu**|INTEGER|NOT NULL|Số SV không có điểm|
|**trang\_thai**|VARCHAR(20)|NOT NULL, CHECK|THANH\_CONG / MOT\_PHAN / LOI|
|**chi\_tiet\_loi**|TEXT|NULL|Thông tin lỗi nếu có|

## **Nhóm D. Phân công hướng dẫn**
### **17. ban\_phan\_cong**
*Bản phân công hướng dẫn của một đợt (nháp → gửi → công bố) (UC: UC07, UC09)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**dot\_id**|BIGINT|FK → dot.id, NOT NULL|Đợt|
|**trang\_thai**|VARCHAR(20)|NOT NULL, CHECK|NHAP / DA\_GUI / DA\_CONG\_BO|
|**nguoi\_tao\_id**|BIGINT|FK → nguoi\_dung.id, NOT NULL|TKhoa soạn|
|**ngay\_gui**|TIMESTAMPTZ|NULL|Ngày gửi cho giảng viên|
|**ngay\_cong\_bo**|TIMESTAMPTZ|NULL|Ngày công bố chính thức|

### **18. phan\_cong\_huong\_dan**
*Từng dòng phân công một hồ sơ cho một giảng viên và phản hồi của HD (UC: UC07, UC08, UC10, UC11)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**ban\_phan\_cong\_id**|BIGINT|FK → ban\_phan\_cong.id, NOT NULL|Bản phân công|
|**ho\_so\_id**|BIGINT|FK → ho\_so.id, NOT NULL|Hồ sơ|
|**giang\_vien\_id**|BIGINT|FK → giang\_vien.id, NOT NULL|Giảng viên được phân|
|**trang\_thai**|VARCHAR(20)|NOT NULL, CHECK|NHAP / CHO\_XAC\_NHAN / DONG\_Y / TU\_CHOI|
|**la\_goi\_y**|BOOLEAN|NOT NULL, mặc định FALSE|TRUE nếu do gợi ý chia đều sinh ra và chưa chỉnh tay|
|**ly\_do\_tu\_choi**|VARCHAR(500)|NULL|Bắt buộc khi TU\_CHOI|
|**ngay\_phan\_hoi**|TIMESTAMPTZ|NULL|Ngày HD phản hồi|

## **Nhóm E. Đề tài**
### **19. de\_tai\_goi\_y**
*Đề tài do giảng viên đưa ra để sinh viên chọn (UC: UC12, UC13)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**dot\_id**|BIGINT|FK → dot.id, NOT NULL|Đợt|
|**giang\_vien\_id**|BIGINT|FK → giang\_vien.id, NOT NULL|Giảng viên đưa ra|
|**ten\_de\_tai**|VARCHAR(300)|NOT NULL|Tên đề tài|
|**mo\_ta**|TEXT|NULL|Mô tả, yêu cầu|
|**so\_luong\_toi\_da**|SMALLINT|NOT NULL, mặc định 1|Số sinh viên có thể chọn|
|**trang\_thai**|VARCHAR(10)|NOT NULL, CHECK|MO / DONG|

### **20. de\_tai**
*Đề tài của một hồ sơ (chọn từ gợi ý hoặc sinh viên đề xuất) và kết quả chốt (UC: UC13, UC14, UC15)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**ho\_so\_id**|BIGINT|FK → ho\_so.id, NOT NULL|Hồ sơ|
|**nguon**|VARCHAR(20)|NOT NULL, CHECK|GV\_DUA\_RA / SV\_DE\_XUAT|
|**de\_tai\_goi\_y\_id**|BIGINT|FK → de\_tai\_goi\_y.id, NULL|Bắt buộc khi nguon = GV\_DUA\_RA|
|**ten\_de\_tai**|VARCHAR(300)|NOT NULL|Tên đề tài|
|**mo\_ta**|TEXT|NULL|Mô tả|
|**trang\_thai**|VARCHAR(15)|NOT NULL, CHECK|CHO\_CHOT / DA\_CHOT / TRA\_LAI|
|**gop\_y\_cua\_gv**|VARCHAR(1000)|NULL|Lý do trả lại, yêu cầu chỉnh sửa|
|**ngay\_gui**|TIMESTAMPTZ|NOT NULL|Ngày sinh viên gửi|
|**ngay\_chot**|TIMESTAMPTZ|NULL|Ngày HD chốt|

## **Nhóm F. Thực hiện và minh chứng**
### **21. thong\_tin\_noi\_thuc\_tap**
*Thông tin liên hệ nơi thực tập, dùng để xác minh điểm nơi thực tập (UC: UC16, UC31)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**ho\_so\_id**|BIGINT|FK → ho\_so.id, UNIQUE, NOT NULL|Hồ sơ|
|**ten\_don\_vi**|VARCHAR(200)|NOT NULL|Tên đơn vị|
|**nguoi\_xac\_nhan**|VARCHAR(150)|NOT NULL|Người ký xác nhận|
|**chuc\_vu**|VARCHAR(100)|NULL|Chức vụ|
|**so\_dien\_thoai**|VARCHAR(20)|NULL|Số điện thoại|
|**email**|VARCHAR(150)|NULL|Email|
|**dia\_chi**|VARCHAR(300)|NULL|Địa chỉ|

### **22. minh\_chung**
*Mỗi lần sinh viên nộp minh chứng tiến độ, báo cáo cuối hoặc giấy xác nhận (UC: UC16, UC17, UC19)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**ho\_so\_id**|BIGINT|FK → ho\_so.id, NOT NULL|Hồ sơ|
|**moc\_id**|BIGINT|FK → dot\_moc\_thoi\_gian.id, NULL|Mốc tương ứng|
|**loai**|VARCHAR(20)|NOT NULL, CHECK|TIEN\_DO / BAO\_CAO\_CUOI / GIAY\_XAC\_NHAN|
|**ghi\_chu**|VARCHAR(1000)|NULL|Ghi chú của sinh viên|
|**ngay\_nop**|TIMESTAMPTZ|NOT NULL, mặc định now()|Ngày nộp|
|**tre\_han**|BOOLEAN|NOT NULL, mặc định FALSE|Nộp sau hạn của mốc|
|**trang\_thai**|VARCHAR(15)|NOT NULL, CHECK|DA\_NOP / CO\_NHAN\_XET|

### **23. tep\_dinh\_kem**
*Tệp thuộc một lần nộp minh chứng (báo cáo, sản phẩm, bản scan giấy xác nhận) (UC: UC16, UC19)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**minh\_chung\_id**|BIGINT|FK → minh\_chung.id, NOT NULL|Lần nộp|
|**ten\_tep**|VARCHAR(255)|NOT NULL|Tên file|
|**duong\_dan**|VARCHAR(500)|NOT NULL|Đường dẫn lưu|
|**loai\_mime**|VARCHAR(100)|NOT NULL|Kiểu tệp (kiểm tra danh sách cho phép)|
|**kich\_thuoc**|BIGINT|NOT NULL, CHECK ≤ giới hạn|Kích thước (byte)|
|**nguoi\_tai\_id**|BIGINT|FK → nguoi\_dung.id, NOT NULL|Người tải|
|**ngay\_tai**|TIMESTAMPTZ|NOT NULL, mặc định now()|Ngày tải|

### **24. nhan\_xet\_minh\_chung**
*Nhận xét của HD cho từng lần nộp (UC: UC17)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**minh\_chung\_id**|BIGINT|FK → minh\_chung.id, NOT NULL|Lần nộp|
|**giang\_vien\_id**|BIGINT|FK → giang\_vien.id, NOT NULL|HD nhận xét|
|**noi\_dung**|TEXT|NOT NULL|Nội dung nhận xét|
|**ngay\_tao**|TIMESTAMPTZ|NOT NULL, mặc định now()|Ngày nhận xét|

## **Nhóm G. Chấm điểm và kết quả**
### **25. hoi\_dong**
*Hội đồng chấm đồ án tốt nghiệp (UC: UC22, UC24)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**dot\_id**|BIGINT|FK → dot.id, NOT NULL|Đợt|
|**ten\_hoi\_dong**|VARCHAR(150)|NOT NULL, UNIQUE(dot\_id, ten\_hoi\_dong)|Tên hội đồng|
|**thoi\_gian\_bao\_ve**|TIMESTAMPTZ|NULL|Thời gian bảo vệ|
|**dia\_diem**|VARCHAR(200)|NULL|Địa điểm|

### **26. thanh\_vien\_hoi\_dong**
*Giảng viên là thành viên của hội đồng (UC: UC22, UC24)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**hoi\_dong\_id**|BIGINT|FK → hoi\_dong.id, NOT NULL|Hội đồng|
|**giang\_vien\_id**|BIGINT|FK → giang\_vien.id, NOT NULL|Thành viên; UNIQUE(hoi\_dong\_id, giang\_vien\_id)|
|**vai\_tro\_trong\_hoi\_dong**|VARCHAR(30)|NULL|Chủ tịch / thư ký / ủy viên (tùy chọn, chờ thầy xác nhận)|

### **27. phan\_cong\_cham**
*Phân công phản biện hoặc hội đồng cho từng hồ sơ (UC: UC22)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**ho\_so\_id**|BIGINT|FK → ho\_so.id, NOT NULL|Hồ sơ|
|**loai**|VARCHAR(15)|NOT NULL, CHECK|PHAN\_BIEN / HOI\_DONG|
|**giang\_vien\_id**|BIGINT|FK → giang\_vien.id, NULL|Giảng viên phản biện; bắt buộc khi PHAN\_BIEN, phải khác HD của hồ sơ|
|**hoi\_dong\_id**|BIGINT|FK → hoi\_dong.id, NULL|Hội đồng; bắt buộc khi HOI\_DONG|
|**nguoi\_phan\_cong\_id**|BIGINT|FK → nguoi\_dung.id, NOT NULL|TKhoa thực hiện|
|**ngay\_phan\_cong**|TIMESTAMPTZ|NOT NULL, mặc định now()|Ngày phân công|

### **28. diem\_thanh\_phan**
*Điểm của từng thành phần do người chấm nhập (UC: UC20, UC21, UC23, UC24)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**ho\_so\_id**|BIGINT|FK → ho\_so.id, NOT NULL|Hồ sơ|
|**thanh\_phan**|VARCHAR(20)|NOT NULL, CHECK|HUONG\_DAN / NOI\_THUC\_TAP / PHAN\_BIEN / HOI\_DONG|
|**nguoi\_cham\_id**|BIGINT|FK → giang\_vien.id, NOT NULL|Người chấm; UNIQUE(ho\_so\_id, thanh\_phan, nguoi\_cham\_id)|
|**diem**|NUMERIC(4,2)|NULL, CHECK 0..10|Điểm hệ 10; sinh viên không có quyền ghi|
|**nhan\_xet**|TEXT|NULL|Nhận xét|
|**trang\_thai**|VARCHAR(10)|NOT NULL, CHECK|NHAP / DA\_GUI (DA\_GUI không sửa nếu không mở lại)|
|**ngay\_gui**|TIMESTAMPTZ|NULL|Ngày gửi điểm|

### **29. xac\_minh\_noi\_thuc\_tap**
*Đối chiếu bản gốc và xác minh điểm nơi thực tập (chống giả mạo) (UC: UC20, UC31)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**ho\_so\_id**|BIGINT|FK → ho\_so.id, UNIQUE, NOT NULL|Hồ sơ|
|**da\_doi\_chieu\_ban\_goc**|BOOLEAN|NOT NULL, mặc định FALSE|HD đã đối chiếu bản gốc có dấu|
|**ngay\_doi\_chieu**|DATE|NULL|Ngày đối chiếu|
|**nguoi\_doi\_chieu\_id**|BIGINT|FK → giang\_vien.id, NULL|HD đối chiếu|
|**can\_xac\_minh**|BOOLEAN|NOT NULL, mặc định FALSE|Hồ sơ cần xác minh với đơn vị|
|**ly\_do\_can\_xac\_minh**|VARCHAR(15)|NULL, CHECK|NGAU\_NHIEN / NGHI\_VAN|
|**ket\_qua\_xac\_minh**|VARCHAR(15)|NULL, CHECK|DA\_XAC\_MINH / NGHI\_VAN|
|**ngay\_xac\_minh**|DATE|NULL|Ngày xác minh|
|**ghi\_chu**|VARCHAR(1000)|NULL|Ghi chú (người liên hệ, cách xác minh)|

### **30. ket\_qua\_ho\_so**
*Điểm cuối và việc lưu hồ sơ (UC: UC25, UC26, UC27)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**ho\_so\_id**|BIGINT|FK → ho\_so.id, UNIQUE, NOT NULL|Hồ sơ|
|**diem\_cuoi**|NUMERIC(4,2)|NOT NULL, CHECK 0..10|Điểm cuối theo trọng số|
|**trong\_so\_su\_dung**|JSONB|NOT NULL|Ảnh chụp trọng số và điểm thành phần lúc chốt|
|**ngay\_chot**|TIMESTAMPTZ|NOT NULL|Ngày chốt|
|**nguoi\_chot\_id**|BIGINT|FK → nguoi\_dung.id, NOT NULL|TKhoa chốt|
|**da\_luu\_tru**|BOOLEAN|NOT NULL, mặc định TRUE|Đã lưu hồ sơ|

## **Nhóm H. Hệ thống**
### **31. thong\_bao**
*Thông báo gửi đến người dùng (UC: UC02)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**nguoi\_nhan\_id**|BIGINT|FK → nguoi\_dung.id, NOT NULL|Người nhận|
|**loai\_su\_kien**|VARCHAR(40)|NOT NULL|Ví dụ: CONG\_BO\_PHAN\_CONG, DE\_TAI\_TRA\_LAI, SAP\_HET\_HAN|
|**tieu\_de**|VARCHAR(200)|NOT NULL|Tiêu đề|
|**noi\_dung**|VARCHAR(1000)|NULL|Nội dung|
|**ho\_so\_id**|BIGINT|FK → ho\_so.id, NULL|Hồ sơ liên quan|
|**da\_doc**|BOOLEAN|NOT NULL, mặc định FALSE|Đã đọc|
|**ngay\_tao**|TIMESTAMPTZ|NOT NULL, mặc định now()|Ngày tạo|

### **32. nhat\_ky\_he\_thong**
*Nhật ký hành động quan trọng; chỉ thêm, không sửa; không ghi nội dung điểm (UC: UC30)*

|**Cột**|**Kiểu**|**Ràng buộc**|**Mô tả**|
| :- | :- | :- | :- |
|**id**|BIGINT|PK, tự tăng|Khóa chính|
|**nguoi\_thuc\_hien\_id**|BIGINT|FK → nguoi\_dung.id, NULL|Người thực hiện (NULL nếu hệ thống)|
|**hanh\_dong**|VARCHAR(50)|NOT NULL|Ví dụ: MO\_DOT, CONG\_BO, CHOT\_DIEM|
|**doi\_tuong\_loai**|VARCHAR(50)|NULL|Bảng đối tượng|
|**doi\_tuong\_id**|BIGINT|NULL|Khóa đối tượng|
|**mo\_ta**|VARCHAR(500)|NULL|Mô tả ngắn (không chứa giá trị điểm)|
|**dia\_chi\_ip**|VARCHAR(45)|NULL|Địa chỉ IP|
|**ngay\_thuc\_hien**|TIMESTAMPTZ|NOT NULL, mặc định now()|Thời điểm|

# **4. Quan hệ giữa các bảng**
*Bảng dưới được sinh trực tiếp từ các khóa ngoại ở mục 3 nên luôn khớp với chi tiết bảng. Quan hệ 1 – 1 là cột có ràng buộc UNIQUE.*

|**STT**|**Bảng cha**|**Bảng con**|**Loại**|**Khóa ngoại ở bảng con**|
| :- | :- | :- | :- | :- |
|1|khoa|bo\_mon|1 – N|khoa\_id|
|2|nguoi\_dung|tai\_khoan\_lien\_ket|1 – N|nguoi\_dung\_id|
|3|nguoi\_dung|sinh\_vien|1 – 1|nguoi\_dung\_id|
|4|khoa|sinh\_vien|1 – N|khoa\_id|
|5|nguoi\_dung|giang\_vien|1 – 1|nguoi\_dung\_id|
|6|khoa|giang\_vien|1 – N|khoa\_id|
|7|bo\_mon|giang\_vien|1 – N|bo\_mon\_id (có thể rỗng)|
|8|nguoi\_dung|nguoi\_dung\_vai\_tro|1 – N|nguoi\_dung\_id|
|9|vai\_tro|nguoi\_dung\_vai\_tro|1 – N|vai\_tro\_id|
|10|khoa|nguoi\_dung\_vai\_tro|1 – N|khoa\_id (có thể rỗng)|
|11|khoa|dot|1 – N|khoa\_id|
|12|nguoi\_dung|dot|1 – N|nguoi\_tao\_id|
|13|dot|dot\_moc\_thoi\_gian|1 – N|dot\_id|
|14|dot|dot\_trong\_so|1 – N|dot\_id|
|15|dot|lan\_nhap\_danh\_sach|1 – N|dot\_id|
|16|nguoi\_dung|lan\_nhap\_danh\_sach|1 – N|nguoi\_tai\_id|
|17|lan\_nhap\_danh\_sach|dong\_nhap\_danh\_sach|1 – N|lan\_nhap\_id|
|18|dot|ho\_so|1 – N|dot\_id|
|19|sinh\_vien|ho\_so|1 – N|sinh\_vien\_id|
|20|giang\_vien|ho\_so|1 – N|giang\_vien\_huong\_dan\_id (có thể rỗng)|
|21|de\_tai|ho\_so|1 – N|de\_tai\_hien\_tai\_id (có thể rỗng)|
|22|ho\_so|diem\_dau\_vao|1 – 1|ho\_so\_id|
|23|dot|lan\_lay\_diem|1 – N|dot\_id|
|24|nguoi\_dung|lan\_lay\_diem|1 – N|nguoi\_thuc\_hien\_id|
|25|dot|ban\_phan\_cong|1 – N|dot\_id|
|26|nguoi\_dung|ban\_phan\_cong|1 – N|nguoi\_tao\_id|
|27|ban\_phan\_cong|phan\_cong\_huong\_dan|1 – N|ban\_phan\_cong\_id|
|28|ho\_so|phan\_cong\_huong\_dan|1 – N|ho\_so\_id|
|29|giang\_vien|phan\_cong\_huong\_dan|1 – N|giang\_vien\_id|
|30|dot|de\_tai\_goi\_y|1 – N|dot\_id|
|31|giang\_vien|de\_tai\_goi\_y|1 – N|giang\_vien\_id|
|32|ho\_so|de\_tai|1 – N|ho\_so\_id|
|33|de\_tai\_goi\_y|de\_tai|1 – N|de\_tai\_goi\_y\_id (có thể rỗng)|
|34|ho\_so|thong\_tin\_noi\_thuc\_tap|1 – 1|ho\_so\_id|
|35|ho\_so|minh\_chung|1 – N|ho\_so\_id|
|36|dot\_moc\_thoi\_gian|minh\_chung|1 – N|moc\_id (có thể rỗng)|
|37|minh\_chung|tep\_dinh\_kem|1 – N|minh\_chung\_id|
|38|nguoi\_dung|tep\_dinh\_kem|1 – N|nguoi\_tai\_id|
|39|minh\_chung|nhan\_xet\_minh\_chung|1 – N|minh\_chung\_id|
|40|giang\_vien|nhan\_xet\_minh\_chung|1 – N|giang\_vien\_id|
|41|dot|hoi\_dong|1 – N|dot\_id|
|42|hoi\_dong|thanh\_vien\_hoi\_dong|1 – N|hoi\_dong\_id|
|43|giang\_vien|thanh\_vien\_hoi\_dong|1 – N|giang\_vien\_id|
|44|ho\_so|phan\_cong\_cham|1 – N|ho\_so\_id|
|45|giang\_vien|phan\_cong\_cham|1 – N|giang\_vien\_id (có thể rỗng)|
|46|hoi\_dong|phan\_cong\_cham|1 – N|hoi\_dong\_id (có thể rỗng)|
|47|nguoi\_dung|phan\_cong\_cham|1 – N|nguoi\_phan\_cong\_id|
|48|ho\_so|diem\_thanh\_phan|1 – N|ho\_so\_id|
|49|giang\_vien|diem\_thanh\_phan|1 – N|nguoi\_cham\_id|
|50|ho\_so|xac\_minh\_noi\_thuc\_tap|1 – 1|ho\_so\_id|
|51|giang\_vien|xac\_minh\_noi\_thuc\_tap|1 – N|nguoi\_doi\_chieu\_id (có thể rỗng)|
|52|ho\_so|ket\_qua\_ho\_so|1 – 1|ho\_so\_id|
|53|nguoi\_dung|ket\_qua\_ho\_so|1 – N|nguoi\_chot\_id|
|54|nguoi\_dung|thong\_bao|1 – N|nguoi\_nhan\_id|
|55|ho\_so|thong\_bao|1 – N|ho\_so\_id (có thể rỗng)|
|56|nguoi\_dung|nhat\_ky\_he\_thong|1 – N|nguoi\_thuc\_hien\_id (có thể rỗng)|

**Các ràng buộc liên bảng không biểu diễn được bằng khóa ngoại đơn:**

- ho\_so.giang\_vien\_huong\_dan\_id chỉ được gán khi phan\_cong\_huong\_dan tương ứng ở trạng thái DONG\_Y.
- ho\_so.de\_tai\_hien\_tai\_id chỉ trỏ tới de\_tai của chính hồ sơ đó và ở trạng thái DA\_CHOT.
- Mỗi hồ sơ có tối đa một dòng phan\_cong\_huong\_dan đang hiệu lực (khác TU\_CHOI); chỉ mục UNIQUE một phần.
- phan\_cong\_cham: loai = PHAN\_BIEN thì giang\_vien\_id có giá trị và hoi\_dong\_id rỗng; loai = HOI\_DONG thì ngược lại (CHECK).
- Phản biện phải khác HD: giang\_vien\_id của phan\_cong\_cham ≠ ho\_so.giang\_vien\_huong\_dan\_id (kiểm tra bằng trigger hoặc tầng ứng dụng).
- Sinh viên, hồ sơ, giảng viên được phân công phải cùng khoa với đợt (kiểm tra ở tầng ứng dụng).
# **5. Giá trị liệt kê**

|**Cột**|**Giá trị**|**Ý nghĩa**|
| :- | :- | :- |
|**dot.loai**|THUC\_TAP, DO\_AN|Loại đợt|
|**dot.trang\_thai**|CHUAN\_BI, PHAN\_CONG, CHOT\_DE\_TAI, THUC\_HIEN, CHAM\_DIEM, HOAN\_TAT|Sáu giai đoạn của đợt|
|**dot.hinh\_thuc\_cham**|PHAN\_BIEN, HOI\_DONG|Cách chấm phần sau hướng dẫn; hội đồng dùng cho đồ án|
|**ho\_so.trang\_thai**|TRONG\_DANH\_SACH, CHO\_XAC\_NHAN, CHO\_CHOT\_DE\_TAI, DANG\_THUC\_HIEN, CHAM\_HUONG\_DAN, CHO\_PHAN\_BIEN, HOAN\_TAT|Bảy trạng thái; nhánh quay lại duy nhất: HD từ chối → TRONG\_DANH\_SACH để TKhoa phân lại|
|**phan\_cong\_huong\_dan.trang\_thai**|NHAP, CHO\_XAC\_NHAN, DONG\_Y, TU\_CHOI|Tiến trình xác nhận của HD|
|**ban\_phan\_cong.trang\_thai**|NHAP, DA\_GUI, DA\_CONG\_BO|Tiến trình của bản phân công|
|**de\_tai.nguon**|GV\_DUA\_RA, SV\_DE\_XUAT|Nguồn đề tài|
|**de\_tai.trang\_thai**|CHO\_CHOT, DA\_CHOT, TRA\_LAI|Kết quả HD xử lý đề tài|
|**minh\_chung.loai**|TIEN\_DO, BAO\_CAO\_CUOI, GIAY\_XAC\_NHAN|Loại lần nộp|
|**diem\_thanh\_phan.thanh\_phan**|HUONG\_DAN, NOI\_THUC\_TAP, PHAN\_BIEN, HOI\_DONG|Thành phần điểm; trùng với dot\_trong\_so.thanh\_phan|
|**diem\_thanh\_phan.trang\_thai**|NHAP, DA\_GUI|Điểm đã gửi thì khóa|
|**diem\_dau\_vao.nguon**|USMART, FILE, KHONG\_CO|Nguồn điểm TB|
|**xac\_minh\_noi\_thuc\_tap.ly\_do\_can\_xac\_minh**|NGAU\_NHIEN, NGHI\_VAN|Lý do chọn xác minh|
|**xac\_minh\_noi\_thuc\_tap.ket\_qua\_xac\_minh**|DA\_XAC\_MINH, NGHI\_VAN|Kết quả xác minh|
|**nguoi\_dung.loai\_nguoi\_dung**|SINH\_VIEN, GIANG\_VIEN, QUAN\_TRI|Loại tài khoản|
|**nguoi\_dung.trang\_thai**|CHUA\_KICH\_HOAT, HOAT\_DONG, KHOA|Tình trạng tài khoản|
|**vai\_tro.ma\_vai\_tro**|TRUONG\_KHOA, GIANG\_VIEN, QUAN\_TRI|Vai trò hệ thống|
|**tai\_khoan\_lien\_ket.nha\_cung\_cap**|USMART, GOOGLE|Nguồn danh tính|
# **6. Quy tắc nghiệp vụ và cách bảo đảm**

|**STT**|**Quy tắc**|**Cách bảo đảm trong CSDL**|
| :- | :- | :- |
|1|Mỗi khoa chỉ thấy dữ liệu của khoa mình|dot.khoa\_id, nguoi\_dung\_vai\_tro.khoa\_id; mọi truy vấn của TKhoa lọc theo khoa|
|2|Mỗi sinh viên chỉ có một hồ sơ trong một đợt|UNIQUE(dot\_id, sinh\_vien\_id) ở ho\_so|
|3|Sinh viên không nhập điểm|diem\_thanh\_phan.nguoi\_cham\_id trỏ giang\_vien; sinh viên không có quyền ghi|
|4|Chỉ TKhoa xem điểm TB đầu vào|Bảng diem\_dau\_vao riêng; phân quyền ở tầng ứng dụng|
|5|Điểm TB lấy một lần, ghi ngày lấy|diem\_dau\_vao.ngay\_lay; lan\_lay\_diem ghi mỗi lần lấy|
|6|Chưa có điểm thì xếp nhóm chia ngẫu nhiên|diem\_dau\_vao.nguon = KHONG\_CO|
|7|Giảng viên không quá số sinh viên tối đa|dot.so\_sv\_toi\_da\_moi\_gv; đếm phan\_cong\_huong\_dan khi lưu bản nháp và khi HD đồng ý|
|8|HD từ chối thì TKhoa phân lại|phan\_cong\_huong\_dan.trang\_thai = TU\_CHOI kèm ly\_do\_tu\_choi; ho\_so quay về TRONG\_DANH\_SACH|
|9|Phản biện khác HD của hồ sơ đó|Kiểm tra giữa phan\_cong\_cham và ho\_so.giang\_vien\_huong\_dan\_id|
|10|Đề tài phải được HD chốt mới sang thực hiện|de\_tai.trang\_thai = DA\_CHOT mới chuyển ho\_so sang DANG\_THUC\_HIEN|
|11|Nộp trễ hạn được đánh dấu|minh\_chung.tre\_han so với dot\_moc\_thoi\_gian.han\_cuoi|
|12|Điểm nơi thực tập có đối chiếu bản gốc|xac\_minh\_noi\_thuc\_tap.da\_doi\_chieu\_ban\_goc; thong\_tin\_noi\_thuc\_tap lưu liên hệ|
|13|Xác minh ngẫu nhiên hoặc khi nghi vấn|xac\_minh\_noi\_thuc\_tap.can\_xac\_minh, ly\_do\_can\_xac\_minh, ket\_qua\_xac\_minh|
|14|Tổng trọng số của đợt bằng 100%|dot\_trong\_so.trong\_so; kiểm tra tổng khi lưu cấu hình|
|15|Không chốt điểm cuối nếu thiếu thành phần|Ứng dụng kiểm tra đủ diem\_thanh\_phan DA\_GUI theo dot\_trong\_so trước khi ghi ket\_qua\_ho\_so|
|16|Đổi trọng số sau này không làm lệch kết quả cũ|ket\_qua\_ho\_so.trong\_so\_su\_dung lưu ảnh chụp|
|17|Ghi nhật ký hành động quan trọng, không ghi nội dung điểm|nhat\_ky\_he\_thong chỉ thêm; mo\_ta không chứa điểm|
|18|Không lưu mật khẩu cổng|nguoi\_dung và tai\_khoan\_lien\_ket không có cột mật khẩu cổng|
# **7. Điểm cần xác nhận**
- Tích hợp USMART là giả định chờ nhà trường đồng ý. Nếu không được: dùng tai\_khoan\_lien\_ket loại GOOGLE với trạng thái duyệt, và diem\_dau\_vao.nguon = FILE (điểm trong file danh sách). Cấu trúc bảng không đổi.
- Điểm TB theo hệ 4 hay hệ 10 (đang để hệ 4 tích lũy theo màn hình bảng điểm).
- Trưởng khoa tạm thời đảm nhiệm mở đợt và tải danh sách; nếu sau này có giáo vụ khoa hoặc Phòng đào tạo có tài khoản thì chỉ thêm vai trò, không đổi bảng.
- Thang điểm và trọng số cụ thể của từng đợt (HD, nơi thực tập, phản biện, hội đồng).
- Hội đồng có cần chủ tịch, thư ký, ủy viên không (cột vai\_tro\_trong\_hoi\_dong đang tùy chọn). Điểm hội đồng là một điểm chung hay từng thành viên chấm riêng (hiện cho phép từng thành viên, UNIQUE theo người chấm).
- Thực tập có dùng phản biện hay chỉ HD chấm; hiện cấu hình ở dot.hinh\_thuc\_cham.
- Một sinh viên được đổi HD sau khi đã công bố hay không (hiện chưa có luồng; cần thêm lịch sử nếu có).
Thiết kế CSDL – trang 
