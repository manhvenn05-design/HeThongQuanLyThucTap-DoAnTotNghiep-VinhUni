from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounts.models import nguoi_dung
from organization.models import khoa, bo_mon, giang_vien, sinh_vien
from dots.models import dot
from hoso.models import ho_so, diem_dau_vao
from phancong.models import ban_phan_cong, phan_cong_huong_dan
from core.constants import (
    DotLoai,
    DotTrangThai,
    LoaiNguoiDung,
    BanPhanCongTrangThai,
    PhanCongHuongDanTrangThai,
)
from organization.selectors import (
    get_current_lecturer,
    get_current_student,
    lay_du_lieu_cong_giang_vien,
    lay_du_lieu_cong_sinh_vien,
)


class OrganizationPortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.khoa = khoa.objects.create(ma_khoa="CNTT", ten_khoa="Khoa Công nghệ Thông tin")
        self.bm = bo_mon.objects.create(khoa=self.khoa, ma_bo_mon="KTPM", ten_bo_mon="Kỹ thuật phần mềm")

        # Giảng viên
        self.nd_gv = nguoi_dung.objects.create(
            ma_dinh_danh_cong="CB_GV01",
            ho_ten="TS. Cao Thanh Sơn",
            email="sonct@vinhuni.edu.vn",
            loai_nguoi_dung=LoaiNguoiDung.GIANG_VIEN
        )
        self.gv = giang_vien.objects.create(
            nguoi_dung=self.nd_gv,
            ma_can_bo="CB_GV01",
            khoa=self.khoa,
            bo_mon=self.bm,
            hoc_vi="TS"
        )
        self.user_gv = User.objects.create_user(
            username="gv_son",
            email="sonct@vinhuni.edu.vn",
            password="password123"
        )

        # Sinh viên
        self.nd_sv = nguoi_dung.objects.create(
            ma_dinh_danh_cong="22A1001",
            ho_ten="Nguyễn Văn An",
            email="an22a1001@student.vinhuni.edu.vn",
            loai_nguoi_dung=LoaiNguoiDung.SINH_VIEN
        )
        self.sv = sinh_vien.objects.create(
            nguoi_dung=self.nd_sv,
            ma_sinh_vien="22A1001",
            lop="63KTPM1",
            khoa=self.khoa
        )
        self.user_sv = User.objects.create_user(
            username="22A1001",
            email="an22a1001@student.vinhuni.edu.vn",
            password="password123"
        )

        # Đợt
        self.dot = dot.objects.create(
            ma_dot="DOT26_HK2_CNTT_01",
            ten_dot="Thực tập tốt nghiệp HK2",
            loai=DotLoai.THUC_TAP,
            hoc_ky=2,
            nam_hoc="2026-2027",
            khoa=self.khoa,
            trang_thai=DotTrangThai.PHAN_CONG,
            so_sv_toi_da_moi_gv=5,
            nguoi_tao=self.nd_gv
        )

        # Hồ sơ sinh viên với điểm đầu vào
        self.hs = ho_so.objects.create(
            dot=self.dot,
            sinh_vien=self.sv
        )
        self.ddv = diem_dau_vao.objects.create(
            ho_so=self.hs,
            diem_tb_he4=3.85,
            tin_chi_tich_luy=120
        )

        # Bản phân công
        self.bpc = ban_phan_cong.objects.create(
            dot=self.dot,
            nguoi_tao=self.nd_gv,
            trang_thai=BanPhanCongTrangThai.DA_GUI
        )
        self.pchd = phan_cong_huong_dan.objects.create(
            ban_phan_cong=self.bpc,
            ho_so=self.hs,
            giang_vien=self.gv,
            trang_thai=PhanCongHuongDanTrangThai.CHO_XAC_NHAN
        )

    def test_get_current_lecturer(self):
        gv = get_current_lecturer(self.user_gv)
        self.assertIsNotNone(gv)
        self.assertEqual(gv.ma_can_bo, "CB_GV01")

    def test_get_current_student(self):
        sv = get_current_student(self.user_sv)
        self.assertIsNotNone(sv)
        self.assertEqual(sv.ma_sinh_vien, "22A1001")

    def test_lay_du_lieu_cong_giang_vien_security_rule_3(self):
        """BẢO MẬT GEMINI.md Rule 3: Giảng viên không được thấy diem_dau_vao"""
        data = lay_du_lieu_cong_giang_vien(self.user_gv, self.dot.id)
        self.assertIn("danh_sach_huong_dan", data)
        self.assertEqual(len(data["danh_sach_huong_dan"]), 1)

        row = data["danh_sach_huong_dan"][0]
        self.assertEqual(row["ma_sv"], "22A1001")
        self.assertNotIn("diem_dau_vao", row)
        self.assertNotIn("diem_tb_he4", row)

        # Kiểm tra cờ can_xac_nhan khi có hồ sơ CHO_XAC_NHAN
        self.assertTrue(data["can_xac_nhan"])
        self.assertEqual(data["cho_xac_nhan_count"], 1)

    def test_lay_du_lieu_cong_sinh_vien_uc11_truoc_khi_cong_bo(self):
        """UC11: Trước khi công bố chính thức, da_co_gvhd = False"""
        data = lay_du_lieu_cong_sinh_vien(self.user_sv, self.dot.id)
        self.assertFalse(data["thong_tin_sv"]["da_co_gvhd"])
        self.assertIsNone(data["thong_tin_sv"]["gvhd_ho_ten"])

    def test_lay_du_lieu_cong_sinh_vien_uc11_sau_khi_cong_bo(self):
        """UC11: Khi đã công bố chính thức và hồ sơ có GVHD, da_co_gvhd = True"""
        self.hs.giang_vien_huong_dan = self.gv
        self.hs.save()

        data = lay_du_lieu_cong_sinh_vien(self.user_sv, self.dot.id)
        self.assertTrue(data["thong_tin_sv"]["da_co_gvhd"])
        self.assertIn("Cao Thanh Sơn", data["thong_tin_sv"]["gvhd_ho_ten"])
        self.assertEqual(data["thong_tin_sv"]["gvhd_ma_cb"], "CB_GV01")

    def test_giangvien_portal_view_renders(self):
        response = self.client.get("/giangvien/")
        self.assertEqual(response.status_code, 200)

    def test_sinhvien_portal_view_renders(self):
        response = self.client.get("/sinhvien/")
        self.assertEqual(response.status_code, 200)
