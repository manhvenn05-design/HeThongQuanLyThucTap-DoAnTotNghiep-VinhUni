from django.test import TestCase
from django.utils import timezone
from accounts.models import nguoi_dung
from organization.models import khoa, sinh_vien
from dots.models import dot
from hoso.models import ho_so, diem_dau_vao
from hoso.selectors import get_hoso_queryset_for_dot, get_hoso_statistics_for_dot
from core.constants import DotLoai, DotTrangThai, HinhThucCham, LoaiNguoiDung


class HosoUC06SelectorTestCase(TestCase):
    def setUp(self):
        # 1. Tạo người dùng Trưởng khoa & Khoa
        self.tk_user = nguoi_dung.objects.create(
            ma_dinh_danh_cong="CB_TK_TEST",
            ho_ten="TS. Trưởng Khoa Test",
            email="truongkhoa@vinhuni.edu.vn",
            loai_nguoi_dung=LoaiNguoiDung.GIANG_VIEN
        )
        self.khoa_ktcn = khoa.objects.create(
            ma_khoa="KTCN",
            ten_khoa="Trường Kỹ thuật và Công nghệ"
        )

        # 2. Tạo đợt
        self.dot_test = dot.objects.create(
            ma_dot="DOT_TEST_2026",
            ten_dot="Đợt đồ án tốt nghiệp thử nghiệm",
            loai=DotLoai.DO_AN,
            hoc_ky=2,
            nam_hoc="2026-2027",
            khoa=self.khoa_ktcn,
            trang_thai=DotTrangThai.CHUAN_BI,
            nguoi_tao=self.tk_user
        )

        # 3. Tạo sinh viên 1: Đủ điều kiện (120 TC, GPA 3.2)
        nd1 = nguoi_dung.objects.create(
            ma_dinh_danh_cong="22A001",
            ho_ten="Sinh Viên Đủ Điều Kiện",
            email="sv1@vinhuni.edu.vn",
            loai_nguoi_dung=LoaiNguoiDung.SINH_VIEN
        )
        sv1 = sinh_vien.objects.create(nguoi_dung=nd1, ma_sinh_vien="22A001", khoa=self.khoa_ktcn, lop="62K1")
        hs1 = ho_so.objects.create(dot=self.dot_test, sinh_vien=sv1)
        diem_dau_vao.objects.create(ho_so=hs1, tin_chi_tich_luy=120, diem_tb_he4=3.20)

        # 4. Tạo sinh viên 2: Thiếu tín chỉ (100 TC, GPA 3.0)
        nd2 = nguoi_dung.objects.create(
            ma_dinh_danh_cong="22A002",
            ho_ten="Sinh Viên Thiếu Tín Chỉ",
            email="sv2@vinhuni.edu.vn",
            loai_nguoi_dung=LoaiNguoiDung.SINH_VIEN
        )
        sv2 = sinh_vien.objects.create(nguoi_dung=nd2, ma_sinh_vien="22A002", khoa=self.khoa_ktcn, lop="62K1")
        hs2 = ho_so.objects.create(dot=self.dot_test, sinh_vien=sv2)
        diem_dau_vao.objects.create(ho_so=hs2, tin_chi_tich_luy=100, diem_tb_he4=3.00)

        # 5. Tạo sinh viên 3: Chưa có điểm USMART
        nd3 = nguoi_dung.objects.create(
            ma_dinh_danh_cong="22A003",
            ho_ten="Sinh Viên Chưa Đồng Bộ",
            email="sv3@vinhuni.edu.vn",
            loai_nguoi_dung=LoaiNguoiDung.SINH_VIEN
        )
        sv3 = sinh_vien.objects.create(nguoi_dung=nd3, ma_sinh_vien="22A003", khoa=self.khoa_ktcn, lop="62K2")
        ho_so.objects.create(dot=self.dot_test, sinh_vien=sv3)

    def test_uc06_statistics_calculation(self):
        stats = get_hoso_statistics_for_dot(self.dot_test)
        self.assertEqual(stats["tong_ho_so"], 3)
        self.assertEqual(stats["co_diem_count"], 2)
        self.assertEqual(stats["thieu_diem_count"], 1)
        self.assertEqual(stats["du_dieu_kien_count"], 1)
        self.assertEqual(stats["chua_du_dieu_kien_count"], 2)

    def test_uc06_filtering_eligible_and_ineligible(self):
        # Lọc tất cả
        qs_all = get_hoso_queryset_for_dot(self.dot_test, status_filter="all")
        self.assertEqual(qs_all.count(), 3)

        # Lọc đủ điều kiện (>=110 TC và >= 2.0)
        qs_eligible = get_hoso_queryset_for_dot(self.dot_test, status_filter="eligible")
        self.assertEqual(qs_eligible.count(), 1)
        self.assertEqual(qs_eligible.first().sinh_vien.ma_sinh_vien, "22A001")

        # Lọc chưa đủ điều kiện
        qs_ineligible = get_hoso_queryset_for_dot(self.dot_test, status_filter="ineligible")
        self.assertEqual(qs_ineligible.count(), 2)
