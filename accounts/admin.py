from django.contrib import admin
from .models import nguoi_dung, tai_khoan_lien_ket, vai_tro, nguoi_dung_vai_tro

@admin.register(nguoi_dung)
class NguoiDungAdmin(admin.ModelAdmin):
    list_display = ("ma_dinh_danh_cong", "ho_ten", "email", "loai_nguoi_dung", "trang_thai", "ngay_tao")
    list_filter = ("loai_nguoi_dung", "trang_thai")
    search_fields = ("ma_dinh_danh_cong", "ho_ten", "email")

@admin.register(tai_khoan_lien_ket)
class TaiKhoanLienKetAdmin(admin.ModelAdmin):
    list_display = ("nguoi_dung", "nha_cung_cap", "ma_ngoai", "trang_thai_duyet", "ngay_lien_ket")
    list_filter = ("nha_cung_cap", "trang_thai_duyet")
    search_fields = ("nguoi_dung__ho_ten", "ma_ngoai")

@admin.register(vai_tro)
class VaiTroAdmin(admin.ModelAdmin):
    list_display = ("ma_vai_tro", "ten_vai_tro", "mo_ta")

@admin.register(nguoi_dung_vai_tro)
class NguoiDungVaiTroAdmin(admin.ModelAdmin):
    list_display = ("nguoi_dung", "vai_tro", "khoa", "hieu_luc_tu", "hieu_luc_den")
    list_filter = ("vai_tro", "khoa")
    search_fields = ("nguoi_dung__ho_ten", "nguoi_dung__ma_dinh_danh_cong")
