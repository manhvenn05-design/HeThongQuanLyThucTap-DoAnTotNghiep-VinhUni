from django.db import models
from django.utils import timezone

class thong_bao(models.Model):
    """Bảng 31: Thông báo gửi đến người dùng trong ứng dụng (UC02)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    nguoi_nhan = models.ForeignKey(
        'accounts.nguoi_dung',
        on_delete=models.CASCADE,
        related_name="cac_thong_bao",
        verbose_name="Người nhận thông báo"
    )
    tieu_de = models.CharField(max_length=200, verbose_name="Tiêu đề thông báo")
    noi_dung = models.TextField(verbose_name="Nội dung thông báo")
    loai = models.CharField(
        max_length=30,
        default="HE_THONG",
        verbose_name="Loại thông báo (PHAN_CONG, DE_TAI, TIEN_DO, DIEM, HE_THONG)"
    )
    duong_dan_dieu_huong = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name="Đường dẫn xem chi tiết (URL nội bộ)"
    )
    da_doc = models.BooleanField(default=False, verbose_name="Đã đọc thông báo")
    ngay_tao = models.DateTimeField(default=timezone.now, verbose_name="Thời điểm gửi")

    class Meta:
        db_table = "thong_bao"
        verbose_name = "Thông báo hệ thống"
        verbose_name_plural = "Danh sách thông báo"
        ordering = ["-ngay_tao"]

    def __str__(self):
        trang_thai_str = "Đã đọc" if self.da_doc else "Chưa đọc"
        return f"[{trang_thai_str}] {self.tieu_de} -> {self.nguoi_nhan.ho_ten}"


class nhat_ky_he_thong(models.Model):
    """Bảng 32: Nhật ký hành động quan trọng; CHỈ THÊM, KHÔNG SỬA; KHÔNG GHI NỘI DUNG ĐIỂM (UC30)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    nguoi_thuc_hien = models.ForeignKey(
        'accounts.nguoi_dung',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cac_nhat_ky_da_ghi",
        verbose_name="Người thực hiện tác động"
    )
    hanh_dong = models.CharField(max_length=100, verbose_name="Hành vi tác động (MÃ_HANH_DONG)")
    doi_tuong_loai = models.CharField(max_length=50, verbose_name="Loại đối tượng (dot, ho_so, ban_phan_cong...)")
    doi_tuong_id = models.BigIntegerField(null=True, blank=True, verbose_name="ID đối tượng bị tác động")
    mo_ta = models.TextField(
        verbose_name="Mô tả hành động",
        help_text="Chỉ ghi hành vi tác động, tuyệt đối KHÔNG ghi giá trị điểm số"
    )
    dia_chi_ip = models.CharField(max_length=45, null=True, blank=True, verbose_name="Địa chỉ IP")
    thoi_gian = models.DateTimeField(default=timezone.now, verbose_name="Thời điểm thực hiện")

    class Meta:
        db_table = "nhat_ky_he_thong"
        verbose_name = "Nhật ký hệ thống (Audit Log)"
        verbose_name_plural = "Nhật ký hệ thống"
        ordering = ["-thoi_gian"]

    def __str__(self):
        nguoi_str = self.nguoi_thuc_hien.ho_ten if self.nguoi_thuc_hien else "Hệ thống"
        return f"{self.thoi_gian.strftime('%d/%m/%Y %H:%M')} | {nguoi_str}: {self.hanh_dong} trên {self.doi_tuong_loai}#{self.doi_tuong_id}"
