from django.db import models
from django.utils import timezone
from core.constants import (
    DotLoai,
    DotTrangThai,
    HinhThucCham,
    LoaiMocThoiGian,
    ThanhPhanDiem,
)

class dot(models.Model):
    """Bảng 9: Một đợt thực tập hoặc đồ án tốt nghiệp của một khoa (UC03)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ma_dot = models.CharField(max_length=30, unique=True, verbose_name="Mã đợt (ví dụ: DOT26_HK2_CNTT_01)")
    ten_dot = models.CharField(max_length=200, verbose_name="Tên đợt thực tập / đồ án")
    loai = models.CharField(
        max_length=20,
        choices=DotLoai.choices,
        default=DotLoai.THUC_TAP,
        verbose_name="Loại đợt"
    )
    hoc_ky = models.PositiveSmallIntegerField(
        choices=[(1, 'Học kỳ 1'), (2, 'Học kỳ 2'), (3, 'Học kỳ hè (Học kỳ 3)')],
        default=1,
        verbose_name="Học kỳ"
    )
    nam_hoc = models.CharField(max_length=9, verbose_name="Năm học (ví dụ: 2026-2027)")
    khoa = models.ForeignKey(
        'organization.khoa',
        on_delete=models.PROTECT,
        related_name="cac_dot",
        verbose_name="Khoa sở hữu đợt"
    )
    trang_thai = models.CharField(
        max_length=20,
        choices=DotTrangThai.choices,
        default=DotTrangThai.CHUAN_BI,
        verbose_name="Trạng thái giai đoạn của đợt"
    )
    so_sv_toi_da_moi_gv = models.PositiveSmallIntegerField(
        default=15,
        verbose_name="Hạn mức sinh viên tối đa cho mỗi GVHD"
    )
    hinh_thuc_cham = models.CharField(
        max_length=20,
        choices=HinhThucCham.choices,
        default=HinhThucCham.PHAN_BIEN,
        verbose_name="Hình thức đánh giá cuối đợt"
    )
    nguoi_tao = models.ForeignKey(
        'accounts.nguoi_dung',
        on_delete=models.PROTECT,
        related_name="cac_dot_da_tao",
        verbose_name="Trưởng khoa mở đợt"
    )
    ngay_tao = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo đợt")

    class Meta:
        db_table = "dot"
        verbose_name = "Đợt thực tập / Đồ án"
        verbose_name_plural = "Danh sách Đợt thực tập & Đồ án"

    def __str__(self):
        return f"{self.ten_dot} ({self.ma_dot}) - {self.get_trang_thai_display()}"


class dot_moc_thoi_gian(models.Model):
    """Bảng 10: Các mốc thời gian của đợt (nộp minh chứng, báo cáo, chấm điểm…) (UC03, UC16, UC18)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    dot = models.ForeignKey(
        dot,
        on_delete=models.CASCADE,
        related_name="cac_moc_thoi_gian",
        verbose_name="Đợt tương ứng"
    )
    ma_moc = models.CharField(max_length=30, verbose_name="Mã mốc")
    ten_moc = models.CharField(max_length=150, verbose_name="Tên mốc sự kiện")
    loai_moc = models.CharField(
        max_length=20,
        choices=LoaiMocThoiGian.choices,
        verbose_name="Loại mốc thời gian"
    )
    thu_tu = models.PositiveSmallIntegerField(default=1, verbose_name="Thứ tự hiển thị")
    han_cuoi = models.DateTimeField(verbose_name="Hạn cuối mốc")

    class Meta:
        db_table = "dot_moc_thoi_gian"
        verbose_name = "Mốc thời gian đợt"
        verbose_name_plural = "Các mốc thời gian đợt"
        ordering = ["thu_tu", "han_cuoi"]
        constraints = [
            models.UniqueConstraint(
                fields=["dot", "ma_moc"],
                name="uq_dot_moc_thoi_gian_dot_ma_moc"
            )
        ]

    def __str__(self):
        return f"{self.dot.ma_dot} - {self.ten_moc} (Hạn: {self.han_cuoi.strftime('%d/%m/%Y %H:%M')})"


class dot_trong_so(models.Model):
    """Bảng 11: Trọng số các thành phần điểm của đợt (UC03, UC26)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    dot = models.ForeignKey(
        dot,
        on_delete=models.CASCADE,
        related_name="cac_trong_so",
        verbose_name="Đợt tương ứng"
    )
    thanh_phan = models.CharField(
        max_length=20,
        choices=ThanhPhanDiem.choices,
        verbose_name="Thành phần điểm"
    )
    trong_so = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Trọng số (%)",
        help_text="Tỷ lệ % của thành phần này trong tổng điểm (0 - 100%)"
    )

    class Meta:
        db_table = "dot_trong_so"
        verbose_name = "Trọng số thành phần điểm"
        verbose_name_plural = "Trọng số thành phần điểm"
        constraints = [
            models.UniqueConstraint(
                fields=["dot", "thanh_phan"],
                name="uq_dot_trong_so_dot_thanh_phan"
            )
        ]

    def __str__(self):
        return f"{self.dot.ma_dot} - {self.get_thanh_phan_display()}: {self.trong_so}%"
