from django.contrib import admin
from .models import de_tai_goi_y, de_tai

@admin.register(de_tai_goi_y)
class DeTaiGoiYAdmin(admin.ModelAdmin):
    list_display = ("ten_de_tai", "giang_vien", "dot", "so_luong_toi_da", "trang_thai")
    list_filter = ("dot", "trang_thai")
    search_fields = ("ten_de_tai", "giang_vien__nguoi_dung__ho_ten")

@admin.register(de_tai)
class DeTaiAdmin(admin.ModelAdmin):
    list_display = ("ten_de_tai", "ho_so", "nguon", "trang_thai", "ngay_gui", "ngay_chot")
    list_filter = ("nguon", "trang_thai")
    search_fields = ("ten_de_tai", "ho_so__sinh_vien__ma_sinh_vien")
