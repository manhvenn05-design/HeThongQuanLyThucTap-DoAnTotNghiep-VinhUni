from django.db import models
from django.utils import timezone
from core.constants import (
    PhanCongChamLoai,
    ThanhPhanDiem,
    DiemThanhPhanTrangThai,
    LyDoXacMinh,
    KetQuaXacMinh,
)

class hoi_dong(models.Model):
    """Bảng 25: Hội đồng chấm đồ án tốt nghiệp (UC22, UC24)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    dot = models.ForeignKey(
        'dots.dot',
        on_delete=models.CASCADE,
        related_name="cac_hoi_dong",
        verbose_name="Đợt tương ứng"
    )
    ten_hoi_dong = models.CharField(max_length=150, verbose_name="Tên hội đồng chấm")
    thoi_gian_bao_ve = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian bảo vệ")
    dia_diem = models.CharField(max_length=200, null=True, blank=True, verbose_name="Địa điểm bảo vệ")

    class Meta:
        db_table = "hoi_dong"
        verbose_name = "Hội đồng chấm đồ án"
        verbose_name_plural = "Các hội đồng chấm đồ án"
        constraints = [
            models.UniqueConstraint(
                fields=["dot", "ten_hoi_dong"],
                name="uq_hoi_dong_dot_ten_hoi_dong"
            )
        ]

    def __str__(self):
        return f"{self.ten_hoi_dong} ({self.dot.ma_dot})"


class thanh_vien_hoi_dong(models.Model):
    """Bảng 26: Giảng viên là thành viên của hội đồng (UC22, UC24)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    hoi_dong = models.ForeignKey(
        hoi_dong,
        on_delete=models.CASCADE,
        related_name="danh_sach_thanh_vien",
        verbose_name="Hội đồng"
    )
    giang_vien = models.ForeignKey(
        'organization.giang_vien',
        on_delete=models.PROTECT,
        related_name="cac_hoi_dong_tham_gia",
        verbose_name="Giảng viên thành viên"
    )
    vai_tro_trong_hoi_dong = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="Vai trò trong hội đồng (Chủ tịch / Thư ký / Ủy viên)"
    )

    class Meta:
        db_table = "thanh_vien_hoi_dong"
        verbose_name = "Thành viên hội đồng"
        verbose_name_plural = "Danh sách thành viên hội đồng"
        constraints = [
            models.UniqueConstraint(
                fields=["hoi_dong", "giang_vien"],
                name="uq_thanh_vien_hoi_dong_hoi_dong_giang_vien"
            )
        ]

    def __str__(self):
        vai_tro_str = f" - {self.vai_tro_trong_hoi_dong}" if self.vai_tro_trong_hoi_dong else ""
        return f"{self.giang_vien.nguoi_dung.ho_ten} ({self.hoi_dong.ten_hoi_dong}{vai_tro_str})"


class phan_cong_cham(models.Model):
    """Bảng 27: Phân công phản biện hoặc hội đồng cho từng hồ sơ (UC22)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ho_so = models.ForeignKey(
        'hoso.ho_so',
        on_delete=models.CASCADE,
        related_name="cac_phan_cong_cham",
        verbose_name="Hồ sơ tương ứng"
    )
    loai = models.CharField(
        max_length=15,
        choices=PhanCongChamLoai.choices,
        verbose_name="Loại phân công đánh giá"
    )
    giang_vien = models.ForeignKey(
        'organization.giang_vien',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="danh_sach_cham_phan_bien",
        verbose_name="Giảng viên phản biện (bắt buộc khi PHAN_BIEN, khác GVHD)"
    )
    hoi_dong = models.ForeignKey(
        hoi_dong,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="danh_sach_ho_so_bao_ve",
        verbose_name="Hội đồng chấm (bắt buộc khi HOI_DONG)"
    )
    nguoi_phan_cong = models.ForeignKey(
        'accounts.nguoi_dung',
        on_delete=models.PROTECT,
        related_name="cac_phan_cong_cham_da_tao",
        verbose_name="Trưởng khoa phân công"
    )
    ngay_phan_cong = models.DateTimeField(default=timezone.now, verbose_name="Thời điểm phân công")

    class Meta:
        db_table = "phan_cong_cham"
        verbose_name = "Phân công phản biện / hội đồng"
        verbose_name_plural = "Phân công phản biện & hội đồng"

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        if self.loai == PhanCongChamLoai.PHAN_BIEN and self.giang_vien:
            gvhd_ids = self.ho_so.cac_phan_cong_huong_dan.filter(
                trang_thai='DONG_Y'
            ).values_list('giang_vien_id', flat=True)
            if self.giang_vien_id in gvhd_ids:
                raise ValidationError("Giảng viên phản biện không được trùng với GVHD của cùng một hồ sơ!")

    def __str__(self):
        nguoi_cham_str = self.giang_vien.nguoi_dung.ho_ten if self.giang_vien else self.hoi_dong.ten_hoi_dong
        return f"Chấm {self.get_loai_display()} cho {self.ho_so.sinh_vien.ma_sinh_vien} -> {nguoi_cham_str}"


class diem_thanh_phan(models.Model):
    """Bảng 28: Điểm của từng thành phần do người chấm nhập (UC20, UC21, UC23, UC24)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ho_so = models.ForeignKey(
        'hoso.ho_so',
        on_delete=models.CASCADE,
        related_name="cac_diem_thanh_phan",
        verbose_name="Hồ sơ tương ứng"
    )
    thanh_phan = models.CharField(
        max_length=20,
        choices=ThanhPhanDiem.choices,
        verbose_name="Thành phần điểm"
    )
    nguoi_cham = models.ForeignKey(
        'organization.giang_vien',
        on_delete=models.PROTECT,
        related_name="cac_diem_da_cham",
        verbose_name="Giảng viên chấm điểm"
    )
    diem = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Điểm số (hệ 10, từ 0 đến 10)"
    )
    nhan_xet = models.TextField(null=True, blank=True, verbose_name="Nhận xét đánh giá")
    trang_thai = models.CharField(
        max_length=10,
        choices=DiemThanhPhanTrangThai.choices,
        default=DiemThanhPhanTrangThai.NHAP,
        verbose_name="Trạng thái điểm"
    )
    ngay_gui = models.DateTimeField(null=True, blank=True, verbose_name="Thời điểm gửi điểm chính thức")

    class Meta:
        db_table = "diem_thanh_phan"
        verbose_name = "Điểm thành phần"
        verbose_name_plural = "Các điểm thành phần"
        constraints = [
            models.UniqueConstraint(
                fields=["ho_so", "thanh_phan", "nguoi_cham"],
                name="uq_diem_thanh_phan_ho_so_thanh_phan_nguoi_cham"
            )
        ]

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        if self.diem is not None and (self.diem < 0 or self.diem > 10):
            raise ValidationError("Điểm số phải nằm trong thang điểm từ 0.00 đến 10.00!")
        if self.pk:
            old = diem_thanh_phan.objects.filter(pk=self.pk).first()
            if old and old.trang_thai == DiemThanhPhanTrangThai.DA_GUI and self.trang_thai == DiemThanhPhanTrangThai.DA_GUI:
                if old.diem != self.diem:
                    raise ValidationError("Điểm đã gửi (DA_GUI) không thể chỉnh sửa nếu không có lệnh mở lại từ Trưởng khoa!")

    def __str__(self):
        diem_str = str(self.diem) if self.diem is not None else "Chưa chấm"
        return f"{self.get_thanh_phan_display()} - {self.ho_so.sinh_vien.ma_sinh_vien}: {diem_str} [{self.get_trang_thai_display()}]"


class xac_minh_noi_thuc_tap(models.Model):
    """Bảng 29: Đối chiếu bản gốc và xác minh điểm nơi thực tập (chống giả mạo) (UC20, UC31)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ho_so = models.OneToOneField(
        'hoso.ho_so',
        on_delete=models.CASCADE,
        related_name="xac_minh_noi_thuc_tap",
        verbose_name="Hồ sơ tương ứng"
    )
    da_doi_chieu_ban_goc = models.BooleanField(default=False, verbose_name="GVHD đã đối chiếu bản gốc có dấu đỏ")
    ngay_doi_chieu = models.DateField(null=True, blank=True, verbose_name="Ngày đối chiếu")
    nguoi_doi_chieu = models.ForeignKey(
        'organization.giang_vien',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cac_lan_doi_chieu_diem",
        verbose_name="GVHD đối chiếu"
    )
    can_xac_minh = models.BooleanField(default=False, verbose_name="Hồ sơ cần xác minh với đơn vị thực tập")
    ly_do_can_xac_minh = models.CharField(
        max_length=15,
        choices=LyDoXacMinh.choices,
        null=True,
        blank=True,
        verbose_name="Lý do cần xác minh"
    )
    ket_qua_xac_minh = models.CharField(
        max_length=15,
        choices=KetQuaXacMinh.choices,
        null=True,
        blank=True,
        verbose_name="Kết quả xác minh"
    )
    ngay_xac_minh = models.DateField(null=True, blank=True, verbose_name="Ngày xác minh")
    ghi_chu = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Ghi chú xác minh (người liên hệ, phương thức)")

    class Meta:
        db_table = "xac_minh_noi_thuc_tap"
        verbose_name = "Xác minh điểm nơi thực tập"
        verbose_name_plural = "Danh sách xác minh nơi thực tập"

    def __str__(self):
        return f"Xác minh nơi thực tập: {self.ho_so.sinh_vien.ma_sinh_vien} - Đối chiếu: {self.da_doi_chieu_ban_goc}"


class ket_qua_ho_so(models.Model):
    """Bảng 30: Điểm cuối và việc lưu hồ sơ (UC25, UC26, UC27)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ho_so = models.OneToOneField(
        'hoso.ho_so',
        on_delete=models.CASCADE,
        related_name="ket_qua_chot",
        verbose_name="Hồ sơ tương ứng"
    )
    diem_cuoi = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Điểm cuối tổng kết theo trọng số (hệ 10)"
    )
    trong_so_su_dung = models.JSONField(
        verbose_name="Ảnh chụp trọng số & điểm thành phần lúc chốt",
        help_text="Snapshot trọng số để thay đổi cấu hình sau này không làm lệch kết quả cũ"
    )
    ngay_chot = models.DateTimeField(default=timezone.now, verbose_name="Thời điểm Trưởng khoa chốt điểm")
    nguoi_chot = models.ForeignKey(
        'accounts.nguoi_dung',
        on_delete=models.PROTECT,
        related_name="cac_ket_qua_da_chot",
        verbose_name="Trưởng khoa chốt"
    )
    da_luu_tru = models.BooleanField(default=True, verbose_name="Đã lưu trữ hồ sơ vĩnh viễn")

    class Meta:
        db_table = "ket_qua_ho_so"
        verbose_name = "Kết quả hồ sơ tổng kết"
        verbose_name_plural = "Kết quả hồ sơ tổng kết"

    def __str__(self):
        return f"Kết quả {self.ho_so.sinh_vien.ma_sinh_vien}: Điểm cuối {self.diem_cuoi}"
