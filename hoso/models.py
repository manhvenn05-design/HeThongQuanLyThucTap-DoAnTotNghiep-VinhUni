from django.db import models
from django.utils import timezone
from core.constants import (
    LanNhapTrangThai,
    DongNhapTrangThai,
    HoSoTrangThai,
    NguonDiemDauVao,
    TrangThaiLayDiem,
)

class lan_nhap_danh_sach(models.Model):
    """Bảng 12: Mỗi lần tải file danh sách của Phòng đào tạo lên hệ thống (UC04, UC05)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    dot = models.ForeignKey(
        'dots.dot',
        on_delete=models.CASCADE,
        related_name="cac_lan_nhap_danh_sach",
        verbose_name="Đợt tương ứng"
    )
    nguoi_tai = models.ForeignKey(
        'accounts.nguoi_dung',
        on_delete=models.PROTECT,
        related_name="cac_lan_tai_file_danh_sach",
        verbose_name="Trưởng khoa tải lên"
    )
    ten_tep = models.CharField(max_length=255, verbose_name="Tên file gốc")
    duong_dan = models.CharField(max_length=500, verbose_name="Đường dẫn lưu trữ file trên đĩa")
    tong_dong = models.IntegerField(default=0, verbose_name="Tổng số dòng đọc được")
    dong_hop_le = models.IntegerField(default=0, verbose_name="Số dòng hợp lệ")
    dong_loi = models.IntegerField(default=0, verbose_name="Số dòng có lỗi")
    trang_thai = models.CharField(
        max_length=20,
        choices=LanNhapTrangThai.choices,
        default=LanNhapTrangThai.XEM_TRUOC,
        verbose_name="Trạng thái lần nhập file"
    )
    ngay_tai = models.DateTimeField(default=timezone.now, verbose_name="Ngày tải file")

    class Meta:
        db_table = "lan_nhap_danh_sach"
        verbose_name = "Lần nhập file danh sách Excel"
        verbose_name_plural = "Lịch sử nhập danh sách Excel"

    def __str__(self):
        return f"{self.dot.ma_dot} - {self.ten_tep} ({self.get_trang_thai_display()})"


class dong_nhap_danh_sach(models.Model):
    """Bảng 13: Từng dòng bóc tách từ file, dùng cho bước xem trước và xác nhận (UC05)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    lan_nhap = models.ForeignKey(
        lan_nhap_danh_sach,
        on_delete=models.CASCADE,
        related_name="cac_dong_boc_tach",
        verbose_name="Thuộc lần nhập"
    )
    so_dong = models.IntegerField(verbose_name="Số thứ tự dòng trong file Excel")
    ma_sinh_vien = models.CharField(max_length=20, verbose_name="Mã sinh viên")
    ho_ten = models.CharField(max_length=150, null=True, blank=True, verbose_name="Họ và tên")
    lop = models.CharField(max_length=50, null=True, blank=True, verbose_name="Lớp")
    diem_tb = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Điểm TB trong file (dự phòng)"
    )
    trang_thai_dong = models.CharField(
        max_length=20,
        choices=DongNhapTrangThai.choices,
        default=DongNhapTrangThai.HOP_LE,
        verbose_name="Trạng thái dòng dữ liệu"
    )
    loi = models.CharField(max_length=300, null=True, blank=True, verbose_name="Mô tả lỗi phát hiện")

    class Meta:
        db_table = "dong_nhap_danh_sach"
        verbose_name = "Dòng bóc tách Excel"
        verbose_name_plural = "Các dòng bóc tách Excel"
        ordering = ["so_dong"]

    def __str__(self):
        return f"Dòng {self.so_dong}: {self.ma_sinh_vien} - {self.ho_ten} [{self.get_trang_thai_dong_display()}]"


class ho_so(models.Model):
    """Bảng 14: Hồ sơ của một sinh viên trong một đợt; BẢNG TRUNG TÂM theo dõi vòng đời (UC05–UC27)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    dot = models.ForeignKey(
        'dots.dot',
        on_delete=models.PROTECT,
        related_name="cac_ho_so",
        verbose_name="Đợt tương ứng"
    )
    sinh_vien = models.ForeignKey(
        'organization.sinh_vien',
        on_delete=models.PROTECT,
        related_name="cac_ho_so_thuc_tap",
        verbose_name="Sinh viên sở hữu hồ sơ"
    )
    trang_thai = models.CharField(
        max_length=25,
        choices=HoSoTrangThai.choices,
        default=HoSoTrangThai.TRONG_DANH_SACH,
        verbose_name="Trạng thái vòng đời hồ sơ"
    )
    giang_vien_huong_dan = models.ForeignKey(
        'organization.giang_vien',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cac_ho_so_huong_dan",
        verbose_name="Giảng viên hướng dẫn chính thức"
    )
    de_tai_hien_tai = models.ForeignKey(
        'detai.de_tai',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ho_so_su_dung",
        verbose_name="Đề tài đã chốt"
    )
    ngay_tao = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo hồ sơ")
    ngay_cap_nhat = models.DateTimeField(auto_now=True, verbose_name="Lần đổi trạng thái gần nhất")

    class Meta:
        db_table = "ho_so"
        verbose_name = "Hồ sơ thực tập / Đồ án"
        verbose_name_plural = "Danh sách Hồ sơ thực tập & Đồ án"
        constraints = [
            models.UniqueConstraint(
                fields=["dot", "sinh_vien"],
                name="uq_ho_so_dot_sinh_vien"
            )
        ]

    def __str__(self):
        return f"Hồ sơ {self.sinh_vien.ma_sinh_vien} - {self.dot.ma_dot} ({self.get_trang_thai_display()})"


class diem_dau_vao(models.Model):
    """Bảng 15: Điểm TB tích lũy dùng gợi ý chia đều; TÁCH BẢNG ĐỂ CHỈ TRƯỞNG KHOA ĐƯỢC XEM (UC06, UC08)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ho_so = models.OneToOneField(
        ho_so,
        on_delete=models.CASCADE,
        related_name="diem_dau_vao",
        verbose_name="Thuộc hồ sơ"
    )
    diem_tb_he4 = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Điểm trung bình tích lũy hệ 4"
    )
    tin_chi_tich_luy = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Số tín chỉ tích lũy"
    )
    ngay_lay = models.DateTimeField(null=True, blank=True, verbose_name="Thời điểm lấy điểm")
    nguon = models.CharField(
        max_length=20,
        choices=NguonDiemDauVao.choices,
        default=NguonDiemDauVao.KHONG_CO,
        verbose_name="Nguồn lấy điểm"
    )

    class Meta:
        db_table = "diem_dau_vao"
        verbose_name = "Điểm trung bình đầu vào (Bảo mật: Chỉ Trưởng khoa)"
        verbose_name_plural = "Điểm trung bình đầu vào"

    def __str__(self):
        diem_str = str(self.diem_tb_he4) if self.diem_tb_he4 is not None else "Chưa có"
        return f"{self.ho_so.sinh_vien.ma_sinh_vien} - Điểm: {diem_str} (Nguồn: {self.get_nguon_display()})"


class lan_lay_diem(models.Model):
    """Bảng 16: Nhật ký mỗi lần lấy điểm TB từ USMART (UC06)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    dot = models.ForeignKey(
        'dots.dot',
        on_delete=models.CASCADE,
        related_name="cac_lan_lay_diem",
        verbose_name="Đợt tương ứng"
    )
    nguoi_thuc_hien = models.ForeignKey(
        'accounts.nguoi_dung',
        on_delete=models.PROTECT,
        related_name="cac_lan_lay_diem_usmart",
        verbose_name="Trưởng khoa thực hiện"
    )
    nguon = models.CharField(
        max_length=20,
        choices=[('USMART', 'Cổng USMART'), ('FILE', 'Bóc tách từ file Excel')],
        default='USMART',
        verbose_name="Nguồn đồng bộ"
    )
    ngay_lay = models.DateTimeField(default=timezone.now, verbose_name="Thời điểm lấy điểm")
    so_sv_co_diem = models.IntegerField(default=0, verbose_name="Số sinh viên lấy được điểm")
    so_sv_thieu = models.IntegerField(default=0, verbose_name="Số sinh viên thiếu điểm")
    trang_thai = models.CharField(
        max_length=20,
        choices=TrangThaiLayDiem.choices,
        default=TrangThaiLayDiem.THANH_CONG,
        verbose_name="Trạng thái kết quả"
    )
    chi_tiet_loi = models.TextField(null=True, blank=True, verbose_name="Chi tiết lỗi nếu có")

    class Meta:
        db_table = "lan_lay_diem"
        verbose_name = "Nhật ký đồng bộ điểm USMART"
        verbose_name_plural = "Lịch sử đồng bộ điểm USMART"

    def __str__(self):
        return f"{self.dot.ma_dot} - {self.get_nguon_display()} lúc {self.ngay_lay.strftime('%d/%m/%Y %H:%M')}"
