from django.db import models
from django.utils import timezone
from core.constants import (
    LoaiNguoiDung,
    NguoiDungTrangThai,
    NhaCungCapLienKet,
    TrangThaiDuyetLienKet,
    MaVaiTro,
)

class nguoi_dung(models.Model):
    """Bảng 3: Tài khoản dùng chung cho mọi người dùng; không lưu mật khẩu cổng (UC01, UC28)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ma_dinh_danh_cong = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Mã định danh cổng (MSSV / Mã CB)",
        help_text="Mã sinh viên hoặc mã cán bộ trên cổng USMART"
    )
    ho_ten = models.CharField(max_length=150, verbose_name="Họ và tên")
    email = models.CharField(max_length=150, unique=True, null=True, blank=True, verbose_name="Email liên hệ")
    so_dien_thoai = models.CharField(max_length=20, null=True, blank=True, verbose_name="Số điện thoại")
    loai_nguoi_dung = models.CharField(
        max_length=20,
        choices=LoaiNguoiDung.choices,
        default=LoaiNguoiDung.SINH_VIEN,
        verbose_name="Loại người dùng"
    )
    trang_thai = models.CharField(
        max_length=20,
        choices=NguoiDungTrangThai.choices,
        default=NguoiDungTrangThai.HOAT_DONG,
        verbose_name="Trạng thái tài khoản"
    )
    lan_dang_nhap_cuoi = models.DateTimeField(null=True, blank=True, verbose_name="Lần đăng nhập cuối")
    ngay_tao = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    class Meta:
        db_table = "nguoi_dung"
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"

    def __str__(self):
        return f"{self.ho_ten} ({self.ma_dinh_danh_cong})"


class tai_khoan_lien_ket(models.Model):
    """Bảng 4: Liên kết tài khoản hệ thống với danh tính bên ngoài (USMART, Google) (UC01)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    nguoi_dung = models.ForeignKey(
        nguoi_dung,
        on_delete=models.CASCADE,
        related_name="cac_tai_khoan_lien_ket",
        verbose_name="Người dùng"
    )
    nha_cung_cap = models.CharField(
        max_length=20,
        choices=NhaCungCapLienKet.choices,
        verbose_name="Nhà cung cấp danh tính"
    )
    ma_ngoai = models.CharField(
        max_length=100,
        verbose_name="Mã định danh phía nhà cung cấp"
    )
    email = models.CharField(max_length=150, null=True, blank=True, verbose_name="Email bên ngoài")
    trang_thai_duyet = models.CharField(
        max_length=20,
        choices=TrangThaiDuyetLienKet.choices,
        default=TrangThaiDuyetLienKet.TU_DONG,
        verbose_name="Trạng thái duyệt liên kết"
    )
    ngay_lien_ket = models.DateTimeField(default=timezone.now, verbose_name="Ngày liên kết")

    class Meta:
        db_table = "tai_khoan_lien_ket"
        verbose_name = "Tài khoản liên kết SSO"
        verbose_name_plural = "Tài khoản liên kết SSO"
        constraints = [
            models.UniqueConstraint(
                fields=["nha_cung_cap", "ma_ngoai"],
                name="uq_tai_khoan_lien_ket_nha_cung_cap_ma_ngoai"
            )
        ]

    def __str__(self):
        return f"{self.nguoi_dung.ho_ten} - {self.get_nha_cung_cap_display()}"


class vai_tro(models.Model):
    """Bảng 7: Danh mục vai trò hệ thống (UC28)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ma_vai_tro = models.CharField(
        max_length=20,
        unique=True,
        choices=MaVaiTro.choices,
        verbose_name="Mã vai trò"
    )
    ten_vai_tro = models.CharField(max_length=100, verbose_name="Tên vai trò")
    mo_ta = models.CharField(max_length=300, null=True, blank=True, verbose_name="Mô tả")

    class Meta:
        db_table = "vai_tro"
        verbose_name = "Vai trò"
        verbose_name_plural = "Danh mục vai trò"

    def __str__(self):
        return f"{self.ten_vai_tro} ({self.ma_vai_tro})"


class nguoi_dung_vai_tro(models.Model):
    """Bảng 8: Gán vai trò cho người dùng, giới hạn theo khoa (UC28)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    nguoi_dung = models.ForeignKey(
        nguoi_dung,
        on_delete=models.CASCADE,
        related_name="phan_quyen_vai_tro",
        verbose_name="Người dùng"
    )
    vai_tro = models.ForeignKey(
        vai_tro,
        on_delete=models.CASCADE,
        related_name="danh_sach_nguoi_dung",
        verbose_name="Vai trò"
    )
    khoa = models.ForeignKey(
        'organization.khoa',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="phan_quyen_vai_tro",
        verbose_name="Phạm vi khoa (NULL nếu là Quản trị viên)"
    )
    hieu_luc_tu = models.DateField(default=timezone.now, verbose_name="Hiệu lực từ ngày")
    hieu_luc_den = models.DateField(null=True, blank=True, verbose_name="Hiệu lực đến ngày")

    class Meta:
        db_table = "nguoi_dung_vai_tro"
        verbose_name = "Phân quyền người dùng theo khoa"
        verbose_name_plural = "Phân quyền người dùng theo khoa"
        constraints = [
            models.UniqueConstraint(
                fields=["nguoi_dung", "vai_tro", "khoa"],
                name="uq_nguoi_dung_vai_tro_khoa"
            )
        ]

    def __str__(self):
        khoa_ten = self.khoa.ten_khoa if self.khoa else "Toàn hệ thống"
        return f"{self.nguoi_dung.ho_ten} - {self.vai_tro.ten_vai_tro} [{khoa_ten}]"
