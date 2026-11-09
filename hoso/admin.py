from django.contrib import admin
from .models import lan_nhap_danh_sach, dong_nhap_danh_sach, ho_so, diem_dau_vao, lan_lay_diem

class DongNhapDanhSachInline(admin.TabularInline):
    model = dong_nhap_danh_sach
    extra = 0
    readonly_fields = ("so_dong", "ma_sinh_vien", "ho_ten", "lop", "diem_tb", "trang_thai_dong", "loi")

@admin.register(lan_nhap_danh_sach)
class LanNhapDanhSachAdmin(admin.ModelAdmin):
    list_display = ("ten_tep", "dot", "tong_dong", "dong_hop_le", "dong_loi", "trang_thai", "ngay_tai")
    list_filter = ("dot", "trang_thai")
    inlines = [DongNhapDanhSachInline]

@admin.register(dong_nhap_danh_sach)
class DongNhapDanhSachAdmin(admin.ModelAdmin):
    list_display = ("so_dong", "ma_sinh_vien", "ho_ten", "lop", "trang_thai_dong", "loi")
    list_filter = ("lan_nhap__dot", "trang_thai_dong")
    search_fields = ("ma_sinh_vien", "ho_ten", "lop")

class DiemDauVaoInline(admin.StackedInline):
    model = diem_dau_vao
    extra = 0

@admin.register(ho_so)
class HoSoAdmin(admin.ModelAdmin):
    list_display = ("ma_sinh_vien", "ho_ten", "dot", "trang_thai", "gvhd", "ngay_cap_nhat")
    list_filter = ("dot", "trang_thai")
    search_fields = ("sinh_vien__ma_sinh_vien", "sinh_vien__nguoi_dung__ho_ten")
    inlines = [DiemDauVaoInline]

    def ma_sinh_vien(self, obj):
        return obj.sinh_vien.ma_sinh_vien
    ma_sinh_vien.short_description = "MSSV"

    def ho_ten(self, obj):
        return obj.sinh_vien.nguoi_dung.ho_ten
    ho_ten.short_description = "Họ và tên"

    def gvhd(self, obj):
        return obj.giang_vien_huong_dan.nguoi_dung.ho_ten if obj.giang_vien_huong_dan else "—"
    gvhd.short_description = "GVHD chính thức"

@admin.register(diem_dau_vao)
class DiemDauVaoAdmin(admin.ModelAdmin):
    list_display = ("ho_so", "diem_tb_he4", "tin_chi_tich_luy", "nguon", "ngay_lay")
    list_filter = ("nguon", "ho_so__dot")
    search_fields = ("ho_so__sinh_vien__ma_sinh_vien",)

@admin.register(lan_lay_diem)
class LanLayDiemAdmin(admin.ModelAdmin):
    list_display = ("dot", "nguon", "so_sv_co_diem", "so_sv_thieu", "trang_thai", "ngay_lay")
    list_filter = ("dot", "trang_thai", "nguon")
