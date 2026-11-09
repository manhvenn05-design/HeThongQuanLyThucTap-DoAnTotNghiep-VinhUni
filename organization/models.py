from django.db import models

class khoa(models.Model):
    """Bảng 1: Danh mục khoa của trường (phạm vi dữ liệu theo khoa) (UC29)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ma_khoa = models.CharField(max_length=20, unique=True, verbose_name="Mã khoa")
    ten_khoa = models.CharField(max_length=200, verbose_name="Tên khoa")
    dang_hoat_dong = models.BooleanField(default=True, verbose_name="Đang hoạt động")

    class Meta:
        db_table = "khoa"
        verbose_name = "Khoa đào tạo"
        verbose_name_plural = "Danh mục Khoa"

    def __str__(self):
        return f"{self.ten_khoa} ({self.ma_khoa})"


class bo_mon(models.Model):
    """Bảng 2: Danh mục bộ môn thuộc khoa (UC29)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    khoa = models.ForeignKey(
        khoa,
        on_delete=models.CASCADE,
        related_name="cac_bo_mon",
        verbose_name="Khoa chủ quản"
    )
    ma_bo_mon = models.CharField(max_length=20, verbose_name="Mã bộ môn")
    ten_bo_mon = models.CharField(max_length=200, verbose_name="Tên bộ môn")
    dang_hoat_dong = models.BooleanField(default=True, verbose_name="Đang hoạt động")

    class Meta:
        db_table = "bo_mon"
        verbose_name = "Bộ môn"
        verbose_name_plural = "Danh mục Bộ môn"
        constraints = [
            models.UniqueConstraint(
                fields=["khoa", "ma_bo_mon"],
                name="uq_bo_mon_khoa_ma_bo_mon"
            )
        ]

    def __str__(self):
        return f"{self.ten_bo_mon} - {self.khoa.ten_khoa}"


class sinh_vien(models.Model):
    """Bảng 5: Thông tin riêng của sinh viên (UC01, UC04, UC05)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    nguoi_dung = models.OneToOneField(
        'accounts.nguoi_dung',
        on_delete=models.CASCADE,
        related_name="thong_tin_sinh_vien",
        verbose_name="Tài khoản người dùng"
    )
    ma_sinh_vien = models.CharField(max_length=20, unique=True, verbose_name="Mã sinh viên")
    lop = models.CharField(max_length=50, null=True, blank=True, verbose_name="Lớp sinh hoạt")
    khoa = models.ForeignKey(
        khoa,
        on_delete=models.PROTECT,
        related_name="danh_sach_sinh_vien",
        verbose_name="Khoa đào tạo"
    )

    class Meta:
        db_table = "sinh_vien"
        verbose_name = "Sinh viên"
        verbose_name_plural = "Hồ sơ Sinh viên"

    def __str__(self):
        return f"{self.ma_sinh_vien} - {self.nguoi_dung.ho_ten} ({self.lop or 'Chưa rõ lớp'})"


class giang_vien(models.Model):
    """Bảng 6: Thông tin riêng của giảng viên (dùng chung cho vai trò HD, PB, HĐ) (UC10, UC22)"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    nguoi_dung = models.OneToOneField(
        'accounts.nguoi_dung',
        on_delete=models.CASCADE,
        related_name="thong_tin_giang_vien",
        verbose_name="Tài khoản người dùng"
    )
    ma_can_bo = models.CharField(max_length=20, unique=True, verbose_name="Mã cán bộ")
    khoa = models.ForeignKey(
        khoa,
        on_delete=models.PROTECT,
        related_name="danh_sach_giang_vien",
        verbose_name="Khoa công tác"
    )
    bo_mon = models.ForeignKey(
        bo_mon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="danh_sach_giang_vien",
        verbose_name="Bộ môn"
    )
    hoc_vi = models.CharField(max_length=50, null=True, blank=True, verbose_name="Học vị, học hàm (ThS, TS, PGS, GS...)")

    class Meta:
        db_table = "giang_vien"
        verbose_name = "Giảng viên"
        verbose_name_plural = "Hồ sơ Giảng viên"

    def __str__(self):
        hoc_vi_str = f"{self.hoc_vi}. " if self.hoc_vi else ""
        return f"{hoc_vi_str}{self.nguoi_dung.ho_ten} ({self.ma_can_bo})"
