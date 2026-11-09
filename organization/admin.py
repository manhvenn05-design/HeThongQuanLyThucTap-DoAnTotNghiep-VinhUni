from django.contrib import admin
from .models import khoa, bo_mon, sinh_vien, giang_vien

@admin.register(khoa)
class KhoaAdmin(admin.ModelAdmin):
    list_display = ("ma_khoa", "ten_khoa", "dang_hoat_dong")
    search_fields = ("ma_khoa", "ten_khoa")

@admin.register(bo_mon)
class BoMonAdmin(admin.ModelAdmin):
    list_display = ("ma_bo_mon", "ten_bo_mon", "khoa", "dang_hoat_dong")
    list_filter = ("khoa", "dang_hoat_dong")
    search_fields = ("ma_bo_mon", "ten_bo_mon")

@admin.register(sinh_vien)
class SinhVienAdmin(admin.ModelAdmin):
    list_display = ("ma_sinh_vien", "ho_ten", "lop", "khoa")
    list_filter = ("khoa", "lop")
    search_fields = ("ma_sinh_vien", "nguoi_dung__ho_ten", "lop")

    def ho_ten(self, obj):
        return obj.nguoi_dung.ho_ten
    ho_ten.short_description = "Họ và tên"

@admin.register(giang_vien)
class GiangVienAdmin(admin.ModelAdmin):
    list_display = ("ma_can_bo", "hoc_vi", "ho_ten", "khoa", "bo_mon")
    list_filter = ("khoa", "bo_mon", "hoc_vi")
    search_fields = ("ma_can_bo", "nguoi_dung__ho_ten")

    def ho_ten(self, obj):
        return obj.nguoi_dung.ho_ten
    ho_ten.short_description = "Họ và tên"
