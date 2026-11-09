from django.contrib import admin
from .models import thong_bao, nhat_ky_he_thong

@admin.register(thong_bao)
class ThongBaoAdmin(admin.ModelAdmin):
    list_display = ("tieu_de", "nguoi_nhan", "loai", "da_doc", "ngay_tao")
    list_filter = ("loai", "da_doc")
    search_fields = ("tieu_de", "nguoi_nhan__ho_ten")

@admin.register(nhat_ky_he_thong)
class NhatKyHeThongAdmin(admin.ModelAdmin):
    list_display = ("thoi_gian", "nguoi_thuc_hien", "hanh_dong", "doi_tuong_loai", "doi_tuong_id", "dia_chi_ip")
    list_filter = ("hanh_dong", "doi_tuong_loai")
    search_fields = ("hanh_dong", "mo_ta", "nguoi_thuc_hien__ho_ten")
    readonly_fields = ("thoi_gian", "nguoi_thuc_hien", "hanh_dong", "doi_tuong_loai", "doi_tuong_id", "mo_ta", "dia_chi_ip")
