from django.db import models
from django.utils import timezone
from core.constants import DeTaiGoiYTrangThai, DeTaiNguon, DeTaiTrangThai

class de_tai_goi_y(models.Model):
    """Bảng 19: Đề tài do giảng viên đưa ra để sinh viên chọn (UC12, UC13)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    dot = models.ForeignKey(
        'dots.dot',
        on_delete=models.CASCADE,
        related_name="cac_de_tai_goi_y",
        verbose_name="Đợt tương ứng"
    )
    giang_vien = models.ForeignKey(
        'organization.giang_vien',
        on_delete=models.PROTECT,
        related_name="cac_de_tai_da_goi_y",
        verbose_name="Giảng viên đề xuất"
    )
    ten_de_tai = models.CharField(max_length=300, verbose_name="Tên đề tài")
    mo_ta = models.TextField(null=True, blank=True, verbose_name="Mô tả, yêu cầu đề tài")
    so_luong_toi_da = models.PositiveSmallIntegerField(default=1, verbose_name="Số lượng sinh viên tối đa có thể chọn")
    trang_thai = models.CharField(
        max_length=10,
        choices=DeTaiGoiYTrangThai.choices,
        default=DeTaiGoiYTrangThai.MO,
        verbose_name="Trạng thái mở/đóng đăng ký"
    )

    class Meta:
        db_table = "de_tai_goi_y"
        verbose_name = "Đề tài gợi ý của GVHD"
        verbose_name_plural = "Danh mục Đề tài gợi ý"

    def __str__(self):
        return f"{self.ten_de_tai} - GV: {self.giang_vien.nguoi_dung.ho_ten} [{self.get_trang_thai_display()}]"


class de_tai(models.Model):
    """Bảng 20: Đề tài của một hồ sơ (chọn từ gợi ý hoặc sinh viên đề xuất) và kết quả chốt (UC13, UC14, UC15)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ho_so = models.ForeignKey(
        'hoso.ho_so',
        on_delete=models.CASCADE,
        related_name="cac_de_tai_dang_ky",
        verbose_name="Hồ sơ tương ứng"
    )
    nguon = models.CharField(
        max_length=20,
        choices=DeTaiNguon.choices,
        verbose_name="Nguồn đề tài"
    )
    de_tai_goi_y = models.ForeignKey(
        de_tai_goi_y,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cac_lua_chon_sinh_vien",
        verbose_name="Gốc đề tài gợi ý (nếu chọn từ GV)"
    )
    ten_de_tai = models.CharField(max_length=300, verbose_name="Tên đề tài")
    mo_ta = models.TextField(null=True, blank=True, verbose_name="Mô tả nội dung, mục tiêu")
    trang_thai = models.CharField(
        max_length=15,
        choices=DeTaiTrangThai.choices,
        default=DeTaiTrangThai.CHO_CHOT,
        verbose_name="Trạng thái chốt đề tài"
    )
    gop_y_cua_gv = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        verbose_name="Góp ý / Yêu cầu chỉnh sửa của GVHD"
    )
    ngay_gui = models.DateTimeField(default=timezone.now, verbose_name="Ngày sinh viên gửi đề tài")
    ngay_chot = models.DateTimeField(null=True, blank=True, verbose_name="Ngày GVHD duyệt chốt")

    class Meta:
        db_table = "de_tai"
        verbose_name = "Đề tài thực tập / đồ án"
        verbose_name_plural = "Đề tài của sinh viên"

    def __str__(self):
        return f"{self.ten_de_tai} ({self.ho_so.sinh_vien.ma_sinh_vien}) - [{self.get_trang_thai_display()}]"
