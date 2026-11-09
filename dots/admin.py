from django.contrib import admin
from .models import dot, dot_moc_thoi_gian, dot_trong_so

class DotMocThoiGianInline(admin.TabularInline):
    model = dot_moc_thoi_gian
    extra = 1

class DotTrongSoInline(admin.TabularInline):
    model = dot_trong_so
    extra = 1

@admin.register(dot)
class DotAdmin(admin.ModelAdmin):
    list_display = ("ma_dot", "ten_dot", "loai", "hoc_ky", "nam_hoc", "khoa", "trang_thai", "hinh_thuc_cham")
    list_filter = ("khoa", "loai", "trang_thai", "nam_hoc")
    search_fields = ("ma_dot", "ten_dot")
    inlines = [DotMocThoiGianInline, DotTrongSoInline]

@admin.register(dot_moc_thoi_gian)
class DotMocThoiGianAdmin(admin.ModelAdmin):
    list_display = ("dot", "ma_moc", "ten_moc", "loai_moc", "thu_tu", "han_cuoi")
    list_filter = ("dot", "loai_moc")

@admin.register(dot_trong_so)
class DotTrongSoAdmin(admin.ModelAdmin):
    list_display = ("dot", "thanh_phan", "trong_so")
    list_filter = ("dot", "thanh_phan")
