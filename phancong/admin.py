from django.contrib import admin
from .models import ban_phan_cong, phan_cong_huong_dan

class PhanCongHuongDanInline(admin.TabularInline):
    model = phan_cong_huong_dan
    extra = 1

@admin.register(ban_phan_cong)
class BanPhanCongAdmin(admin.ModelAdmin):
    list_display = ("dot", "trang_thai", "nguoi_tao", "ngay_gui", "ngay_cong_bo")
    list_filter = ("dot", "trang_thai")
    inlines = [PhanCongHuongDanInline]

@admin.register(phan_cong_huong_dan)
class PhanCongHuongDanAdmin(admin.ModelAdmin):
    list_display = ("ho_so", "giang_vien", "trang_thai", "la_goi_y", "ngay_phan_hoi")
    list_filter = ("trang_thai", "la_goi_y", "ban_phan_cong__dot")
    search_fields = ("ho_so__sinh_vien__ma_sinh_vien", "giang_vien__nguoi_dung__ho_ten")
