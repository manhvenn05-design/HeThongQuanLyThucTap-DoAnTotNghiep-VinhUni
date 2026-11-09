from django.db import models
from django.utils import timezone
from core.constants import BanPhanCongTrangThai, PhanCongHuongDanTrangThai

class ban_phan_cong(models.Model):
    """Bảng 17: Bản phân công hướng dẫn của một đợt (nháp -> gửi -> công bố) (UC07, UC09)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    dot = models.ForeignKey(
        'dots.dot',
        on_delete=models.CASCADE,
        related_name="cac_ban_phan_cong",
        verbose_name="Đợt tương ứng"
    )
    trang_thai = models.CharField(
        max_length=20,
        choices=BanPhanCongTrangThai.choices,
        default=BanPhanCongTrangThai.NHAP,
        verbose_name="Trạng thái bản phân công"
    )
    nguoi_tao = models.ForeignKey(
        'accounts.nguoi_dung',
        on_delete=models.PROTECT,
        related_name="cac_ban_phan_cong_da_soan",
        verbose_name="Trưởng khoa soạn bản phân công"
    )
    ngay_gui = models.DateTimeField(null=True, blank=True, verbose_name="Ngày gửi cho giảng viên")
    ngay_cong_bo = models.DateTimeField(null=True, blank=True, verbose_name="Ngày công bố chính thức")

    class Meta:
        db_table = "ban_phan_cong"
        verbose_name = "Bản phân công hướng dẫn"
        verbose_name_plural = "Các bản phân công hướng dẫn"

    def __str__(self):
        return f"Bản phân công {self.dot.ma_dot} ({self.get_trang_thai_display()})"


class phan_cong_huong_dan(models.Model):
    """Bảng 18: Từng dòng phân công một hồ sơ cho một giảng viên và phản hồi của HD (UC07, UC08, UC10, UC11)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ban_phan_cong = models.ForeignKey(
        ban_phan_cong,
        on_delete=models.CASCADE,
        related_name="cac_dong_phan_cong",
        verbose_name="Thuộc bản phân công"
    )
    ho_so = models.ForeignKey(
        'hoso.ho_so',
        on_delete=models.CASCADE,
        related_name="cac_phan_cong_huong_dan",
        verbose_name="Hồ sơ sinh viên"
    )
    giang_vien = models.ForeignKey(
        'organization.giang_vien',
        on_delete=models.PROTECT,
        related_name="danh_sach_huong_dan_duoc_phan",
        verbose_name="Giảng viên được phân công"
    )
    trang_thai = models.CharField(
        max_length=20,
        choices=PhanCongHuongDanTrangThai.choices,
        default=PhanCongHuongDanTrangThai.NHAP,
        verbose_name="Trạng thái xác nhận của GVHD"
    )
    la_goi_y = models.BooleanField(
        default=False,
        verbose_name="Do thuật toán chia đều gợi ý",
        help_text="TRUE nếu do hệ thống chia đều sinh ra và Trưởng khoa chưa chỉnh tay"
    )
    ly_do_tu_choi = models.CharField(max_length=500, null=True, blank=True, verbose_name="Lý do từ chối (bắt buộc khi từ chối)")
    ngay_phan_hoi = models.DateTimeField(null=True, blank=True, verbose_name="Thời điểm GVHD phản hồi")

    class Meta:
        db_table = "phan_cong_huong_dan"
        verbose_name = "Dòng phân công GVHD"
        verbose_name_plural = "Chi tiết phân công GVHD"
        constraints = [
            models.UniqueConstraint(
                fields=["ban_phan_cong", "ho_so"],
                name="uq_phan_cong_huong_dan_ban_phan_cong_ho_so"
            )
        ]

    def __str__(self):
        return f"Phân công {self.ho_so.sinh_vien.ma_sinh_vien} -> {self.giang_vien.nguoi_dung.ho_ten} [{self.get_trang_thai_display()}]"
