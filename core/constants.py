"""
Định nghĩa toàn bộ Enums và Choices chuẩn hóa 100% theo CSDL đặc tả.
Chứa các nhãn (labels) tiếng Việt tự nhiên, thân thiện cho UI.
"""
from django.db import models

class LoaiNguoiDung(models.TextChoices):
    SINH_VIEN = 'SINH_VIEN', 'Sinh viên'
    GIANG_VIEN = 'GIANG_VIEN', 'Giảng viên'
    QUAN_TRI = 'QUAN_TRI', 'Quản trị hệ thống'

class NguoiDungTrangThai(models.TextChoices):
    CHUA_KICH_HOAT = 'CHUA_KICH_HOAT', 'Chưa kích hoạt'
    HOAT_DONG = 'HOAT_DONG', 'Đang hoạt động'
    KHOA = 'KHOA', 'Bị khóa'

class NhaCungCapLienKet(models.TextChoices):
    USMART = 'USMART', 'Cổng USMART'
    GOOGLE = 'GOOGLE', 'Tài khoản Google'

class TrangThaiDuyetLienKet(models.TextChoices):
    TU_DONG = 'TU_DONG', 'Tự động'
    CHO_DUYET = 'CHO_DUYET', 'Chờ duyệt'
    DA_DUYET = 'DA_DUYET', 'Đã duyệt'
    TU_CHOI = 'TU_CHOI', 'Từ chối'

class MaVaiTro(models.TextChoices):
    TRUONG_KHOA = 'TRUONG_KHOA', 'Trưởng khoa'
    GIANG_VIEN = 'GIANG_VIEN', 'Giảng viên'
    QUAN_TRI = 'QUAN_TRI', 'Quản trị viên'

class DotLoai(models.TextChoices):
    THUC_TAP = 'THUC_TAP', 'Thực tập tốt nghiệp'
    DO_AN = 'DO_AN', 'Đồ án tốt nghiệp'

class DotTrangThai(models.TextChoices):
    CHUAN_BI = 'CHUAN_BI', 'Chuẩn bị đợt'
    PHAN_CONG = 'PHAN_CONG', 'Phân công hướng dẫn'
    CHOT_DE_TAI = 'CHOT_DE_TAI', 'Chọn & Chốt đề tài'
    THUC_HIEN = 'THUC_HIEN', 'Đang thực hiện'
    CHAM_DIEM = 'CHAM_DIEM', 'Đang chấm điểm'
    HOAN_TAT = 'HOAN_TAT', 'Đã hoàn tất & Lưu trữ'

class HinhThucCham(models.TextChoices):
    PHAN_BIEN = 'PHAN_BIEN', 'Chấm phản biện'
    HOI_DONG = 'HOI_DONG', 'Chấm hội đồng'

class LoaiMocThoiGian(models.TextChoices):
    PHAN_CONG = 'PHAN_CONG', 'Hạn phân công hướng dẫn'
    CHOT_DE_TAI = 'CHOT_DE_TAI', 'Hạn chốt đề tài'
    NOP_TIEN_DO = 'NOP_TIEN_DO', 'Hạn nộp minh chứng tiến độ'
    NOP_BAO_CAO = 'NOP_BAO_CAO', 'Hạn nộp báo cáo / khóa luận cuối'
    CHAM_DIEM = 'CHAM_DIEM', 'Hạn chấm điểm'

class ThanhPhanDiem(models.TextChoices):
    HUONG_DAN = 'HUONG_DAN', 'Điểm đánh giá GVHD'
    NOI_THUC_TAP = 'NOI_THUC_TAP', 'Điểm đơn vị thực tập'
    PHAN_BIEN = 'PHAN_BIEN', 'Điểm phản biện'
    HOI_DONG = 'HOI_DONG', 'Điểm hội đồng bảo vệ'

class LanNhapTrangThai(models.TextChoices):
    XEM_TRUOC = 'XEM_TRUOC', 'Đang xem trước'
    DA_XAC_NHAN = 'DA_XAC_NHAN', 'Đã xác nhận'
    HUY = 'HUY', 'Đã hủy'

class DongNhapTrangThai(models.TextChoices):
    HOP_LE = 'HOP_LE', 'Hợp lệ'
    TRUNG = 'TRUNG', 'Bị trùng lặp'
    LOI = 'LOI', 'Lỗi dữ liệu'

class HoSoTrangThai(models.TextChoices):
    TRONG_DANH_SACH = 'TRONG_DANH_SACH', 'Trong danh sách đợt'
    CHO_XAC_NHAN = 'CHO_XAC_NHAN', 'Chờ GVHD tiếp nhận'
    CHO_CHOT_DE_TAI = 'CHO_CHOT_DE_TAI', 'Chờ chốt đề tài'
    DANG_THUC_HIEN = 'DANG_THUC_HIEN', 'Đang thực hiện'
    CHAM_HUONG_DAN = 'CHAM_HUONG_DAN', 'Chờ GVHD chấm'
    CHO_PHAN_BIEN = 'CHO_PHAN_BIEN', 'Chờ chấm PB / Hội đồng'
    HOAN_TAT = 'HOAN_TAT', 'Đã hoàn tất & Lưu trữ'

class NguonDiemDauVao(models.TextChoices):
    USMART = 'USMART', 'Đồng bộ từ USMART'
    FILE = 'FILE', 'Bóc tách từ file'
    KHONG_CO = 'KHONG_CO', 'Chưa có điểm'

class TrangThaiLayDiem(models.TextChoices):
    THANH_CONG = 'THANH_CONG', 'Thành công'
    MOT_PHAN = 'MOT_PHAN', 'Thành công một phần'
    LOI = 'LOI', 'Gặp lỗi'

class BanPhanCongTrangThai(models.TextChoices):
    NHAP = 'NHAP', 'Bản thảo (Nháp)'
    DA_GUI = 'DA_GUI', 'Đã gửi cho GVHD'
    DA_CONG_BO = 'DA_CONG_BO', 'Đã công bố chính thức'

class PhanCongHuongDanTrangThai(models.TextChoices):
    NHAP = 'NHAP', 'Dự thảo'
    CHO_XAC_NHAN = 'CHO_XAC_NHAN', 'Chờ GVHD xác nhận'
    DONG_Y = 'DONG_Y', 'Đồng ý tiếp nhận'
    TU_CHOI = 'TU_CHOI', 'Từ chối tiếp nhận'

class DeTaiGoiYTrangThai(models.TextChoices):
    MO = 'MO', 'Đang mở đăng ký'
    DONG = 'DONG', 'Đã đóng'

class DeTaiNguon(models.TextChoices):
    GV_DUA_RA = 'GV_DUA_RA', 'Đề tài do GVHD gợi ý'
    SV_DE_XUAT = 'SV_DE_XUAT', 'Đề tài do sinh viên đề xuất'

class DeTaiTrangThai(models.TextChoices):
    CHO_CHOT = 'CHO_CHOT', 'Chờ GVHD duyệt'
    DA_CHOT = 'DA_CHOT', 'Đã duyệt chốt'
    TRA_LAI = 'TRA_LAI', 'Trả lại yêu cầu sửa'

class MinhChungLoai(models.TextChoices):
    TIEN_DO = 'TIEN_DO', 'Minh chứng tiến độ định kỳ'
    BAO_CAO_CUOI = 'BAO_CAO_CUOI', 'Báo cáo / Khóa luận cuối đợt'
    GIAY_XAC_NHAN = 'GIAY_XAC_NHAN', 'Giấy xác nhận của đơn vị thực tập'

class MinhChungTrangThai(models.TextChoices):
    DA_NOP = 'DA_NOP', 'Đã nộp, chờ nhận xét'
    CO_NHAN_XET = 'CO_NHAN_XET', 'Đã có nhận xét'

class PhanCongChamLoai(models.TextChoices):
    PHAN_BIEN = 'PHAN_BIEN', 'Phản biện độc lập'
    HOI_DONG = 'HOI_DONG', 'Hội đồng chấm bảo vệ'

class DiemThanhPhanTrangThai(models.TextChoices):
    NHAP = 'NHAP', 'Bản nháp'
    DA_GUI = 'DA_GUI', 'Đã gửi chính thức'

class LyDoXacMinh(models.TextChoices):
    NGAU_NHIEN = 'NGAU_NHIEN', 'Kiểm tra ngẫu nhiên'
    NGHI_VAN = 'NGHI_VAN', 'Phát hiện nghi vấn'

class KetQuaXacMinh(models.TextChoices):
    DA_XAC_NHAN = 'DA_XAC_NHAN', 'Đã xác minh chính xác'
    NGHI_VAN = 'NGHI_VAN', 'Nghi vấn / Điểm không khớp'
