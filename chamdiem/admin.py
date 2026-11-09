from django.contrib import admin
from .models import (
    hoi_dong,
    thanh_vien_hoi_dong,
    phan_cong_cham,
    diem_thanh_phan,
    xac_minh_noi_thuc_tap,
    ket_qua_ho_so,
)

class ThanhVienHoiDongInline(admin.TabularInline):
    model = thanh_vien_hoi_dong
    extra = 1

@admin.register(hoi_dong)
class HoiDongAdmin(admin.ModelAdmin):
    list_display = ("ten_hoi_dong", "dot", "thoi_gian_bao_ve", "dia_diem")
    list_filter = ("dot",)
    inlines = [ThanhVienHoiDongInline]

@admin.register(thanh_vien_hoi_dong)
class ThanhVienHoiDongAdmin(admin.ModelAdmin):
    list_display = ("hoi_dong", "giang_vien", "vai_tro_trong_hoi_dong")
    list_filter = ("hoi_dong__dot",)

@admin.register(phan_cong_cham)
class PhanCongChamAdmin(admin.ModelAdmin):
    list_display = ("ho_so", "loai", "giang_vien", "hoi_dong", "ngay_phan_cong")
    list_filter = ("loai", "ho_so__dot")

@admin.register(diem_thanh_phan)
class DiemThanhPhanAdmin(admin.ModelAdmin):
    list_display = ("ho_so", "thanh_phan", "nguoi_cham", "diem", "trang_thai", "ngay_gui")
    list_filter = ("thanh_phan", "trang_thai", "ho_so__dot")

@admin.register(xac_minh_noi_thuc_tap)
class XacMinhNoiThucTapAdmin(admin.ModelAdmin):
    list_display = ("ho_so", "da_doi_chieu_ban_goc", "can_xac_minh", "ket_qua_xac_minh", "ngay_xac_minh")
    list_filter = ("da_doi_chieu_ban_goc", "can_xac_minh", "ket_qua_xac_minh")

@admin.register(ket_qua_ho_so)
class KetQuaHoSoAdmin(admin.ModelAdmin):
    list_display = ("ho_so", "diem_cuoi", "ngay_chot", "nguoi_chot", "da_luu_tru")
    list_filter = ("da_luu_tru", "ho_so__dot")
