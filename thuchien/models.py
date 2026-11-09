from django.db import models
from django.utils import timezone
from core.constants import MinhChungLoai, MinhChungTrangThai

class thong_tin_noi_thuc_tap(models.Model):
    """Bảng 21: Thông tin liên hệ nơi thực tập, dùng để xác minh điểm nơi thực tập (UC16, UC31)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ho_so = models.OneToOneField(
        'hoso.ho_so',
        on_delete=models.CASCADE,
        related_name="thong_tin_noi_thuc_tap",
        verbose_name="Thuộc hồ sơ"
    )
    ten_don_vi = models.CharField(max_length=200, verbose_name="Tên cơ quan, doanh nghiệp thực tập")
    nguoi_xac_nhan = models.CharField(max_length=150, verbose_name="Người phụ trách / ký xác nhận")
    chuc_vu = models.CharField(max_length=100, null=True, blank=True, verbose_name="Chức vụ người xác nhận")
    so_dien_thoai = models.CharField(max_length=20, null=True, blank=True, verbose_name="Số điện thoại liên hệ")
    email = models.CharField(max_length=150, null=True, blank=True, verbose_name="Email liên hệ")
    dia_chi = models.CharField(max_length=300, null=True, blank=True, verbose_name="Địa chỉ đơn vị thực tập")

    class Meta:
        db_table = "thong_tin_noi_thuc_tap"
        verbose_name = "Thông tin nơi thực tập"
        verbose_name_plural = "Thông tin các đơn vị thực tập"

    def __str__(self):
        return f"{self.ten_don_vi} ({self.ho_so.sinh_vien.ma_sinh_vien})"


class minh_chung(models.Model):
    """Bảng 22: Mỗi lần sinh viên nộp minh chứng tiến độ, báo cáo cuối hoặc giấy xác nhận (UC16, UC17, UC19)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ho_so = models.ForeignKey(
        'hoso.ho_so',
        on_delete=models.CASCADE,
        related_name="cac_lan_nop_minh_chung",
        verbose_name="Hồ sơ tương ứng"
    )
    moc = models.ForeignKey(
        'dots.dot_moc_thoi_gian',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cac_minh_chung_nop",
        verbose_name="Thuộc mốc thời gian"
    )
    loai = models.CharField(
        max_length=20,
        choices=MinhChungLoai.choices,
        verbose_name="Loại minh chứng nộp"
    )
    ghi_chu = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Ghi chú của sinh viên")
    ngay_nop = models.DateTimeField(default=timezone.now, verbose_name="Thời điểm nộp")
    tre_han = models.BooleanField(default=False, verbose_name="Nộp trễ hạn quy định")
    trang_thai = models.CharField(
        max_length=15,
        choices=MinhChungTrangThai.choices,
        default=MinhChungTrangThai.DA_NOP,
        verbose_name="Trạng thái minh chứng"
    )

    class Meta:
        db_table = "minh_chung"
        verbose_name = "Minh chứng tiến độ / Báo cáo"
        verbose_name_plural = "Các lần nộp minh chứng"
        ordering = ["-ngay_nop"]

    def __str__(self):
        tre_str = " (Trễ hạn)" if self.tre_han else ""
        return f"{self.get_loai_display()} - {self.ho_so.sinh_vien.ma_sinh_vien}{tre_str}"


class tep_dinh_kem(models.Model):
    """Bảng 23: Tệp thuộc một lần nộp minh chứng (báo cáo, sản phẩm, bản scan giấy xác nhận) (UC16, UC19)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    minh_chung = models.ForeignKey(
        minh_chung,
        on_delete=models.CASCADE,
        related_name="cac_tep_dinh_kem",
        verbose_name="Thuộc lần nộp minh chứng"
    )
    ten_tep = models.CharField(max_length=255, verbose_name="Tên file gốc")
    duong_dan = models.CharField(max_length=500, verbose_name="Đường dẫn lưu file trên đĩa")
    loai_mime = models.CharField(max_length=100, verbose_name="Định dạng tệp (MIME type)")
    kich_thuoc = models.BigIntegerField(verbose_name="Kích thước file (bytes)")
    nguoi_tai = models.ForeignKey(
        'accounts.nguoi_dung',
        on_delete=models.PROTECT,
        related_name="cac_tep_da_tai_len",
        verbose_name="Người tải file lên"
    )
    ngay_tai = models.DateTimeField(default=timezone.now, verbose_name="Thời điểm tải lên")

    class Meta:
        db_table = "tep_dinh_kem"
        verbose_name = "Tệp đính kèm"
        verbose_name_plural = "Các tệp đính kèm"

    def __str__(self):
        return f"{self.ten_tep} ({self.kich_thuoc} bytes)"


class nhan_xet_minh_chung(models.Model):
    """Bảng 24: Nhận xét của HD cho từng lần nộp (UC17)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    minh_chung = models.ForeignKey(
        minh_chung,
        on_delete=models.CASCADE,
        related_name="cac_nhan_xet_cua_gv",
        verbose_name="Lần nộp minh chứng"
    )
    giang_vien = models.ForeignKey(
        'organization.giang_vien',
        on_delete=models.PROTECT,
        related_name="cac_nhan_xet_da_dua",
        verbose_name="Giảng viên hướng dẫn nhận xét"
    )
    noi_dung = models.TextField(verbose_name="Nội dung nhận xét, đánh giá tiến độ")
    ngay_tao = models.DateTimeField(default=timezone.now, verbose_name="Thời điểm nhận xét")

    class Meta:
        db_table = "nhan_xet_minh_chung"
        verbose_name = "Nhận xét minh chứng"
        verbose_name_plural = "Các nhận xét minh chứng"

    def __str__(self):
        return f"Nhận xét của {self.giang_vien.nguoi_dung.ho_ten} cho {self.minh_chung}"
