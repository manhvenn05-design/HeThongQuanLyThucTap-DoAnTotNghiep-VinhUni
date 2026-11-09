from django.contrib import admin
from .models import thong_tin_noi_thuc_tap, minh_chung, tep_dinh_kem, nhan_xet_minh_chung

@admin.register(thong_tin_noi_thuc_tap)
class ThongTinNoiThucTapAdmin(admin.ModelAdmin):
    list_display = ("ten_don_vi", "nguoi_xac_nhan", "chuc_vu", "so_dien_thoai", "email")
    search_fields = ("ten_don_vi", "ho_so__sinh_vien__ma_sinh_vien")

class TepDinhKemInline(admin.TabularInline):
    model = tep_dinh_kem
    extra = 0

class NhanXetMinhChungInline(admin.TabularInline):
    model = nhan_xet_minh_chung
    extra = 1

@admin.register(minh_chung)
class MinhChungAdmin(admin.ModelAdmin):
    list_display = ("ho_so", "loai", "moc", "tre_han", "trang_thai", "ngay_nop")
    list_filter = ("loai", "tre_han", "trang_thai")
    search_fields = ("ho_so__sinh_vien__ma_sinh_vien",)
    inlines = [TepDinhKemInline, NhanXetMinhChungInline]

@admin.register(tep_dinh_kem)
class TepDinhKemAdmin(admin.ModelAdmin):
    list_display = ("ten_tep", "minh_chung", "kich_thuoc", "nguoi_tai", "ngay_tai")

@admin.register(nhan_xet_minh_chung)
class NhanXetMinhChungAdmin(admin.ModelAdmin):
    list_display = ("minh_chung", "giang_vien", "ngay_tao")
