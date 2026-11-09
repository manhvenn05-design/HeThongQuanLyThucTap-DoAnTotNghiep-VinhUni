from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import nguoi_dung, vai_tro, nguoi_dung_vai_tro
from organization.models import khoa, bo_mon, giang_vien, sinh_vien
from dots.models import dot
from hoso.models import ho_so
from phancong.models import phan_cong_huong_dan, ban_phan_cong
from chamdiem.models import phan_cong_cham, diem_thanh_phan
from core.constants import (
    DotTrangThai,
    HoSoTrangThai,
    BanPhanCongTrangThai,
    PhanCongHuongDanTrangThai,
    PhanCongChamLoai,
    ThanhPhanDiem,
    DiemThanhPhanTrangThai,
)


class ChamDiemSecurityTestCase(TestCase):
    """Kiểm tra các ràng buộc bảo mật & liêm chính dữ liệu theo GEMINI.md"""

    def setUp(self):
        # 1. Tạo khoa & bộ môn
        self.khoa_cntt = khoa.objects.create(
            ma_khoa="CNTT",
            ten_khoa="Khoa Công nghệ Thông tin"
        )
        self.bo_mon_ktpm = bo_mon.objects.create(
            khoa=self.khoa_cntt,
            ma_bo_mon="KTPM",
            ten_bo_mon="Kỹ thuật phần mềm"
        )

        # 2. Tạo người dùng Trưởng khoa & Giảng viên
        self.user_dean = nguoi_dung.objects.create(
            ma_dinh_danh_cong="CB_TK01",
            ho_ten="TS. Phan Anh Phong",
            email="dean@vinhuni.edu.vn",
            loai_nguoi_dung="CAN_BO"
        )
        self.user_gv1 = nguoi_dung.objects.create(
            ma_dinh_danh_cong="CB_GV01",
            ho_ten="TS. Cao Thanh Sơn",
            email="gv1@vinhuni.edu.vn",
            loai_nguoi_dung="CAN_BO"
        )
        self.user_gv2 = nguoi_dung.objects.create(
            ma_dinh_danh_cong="CB_GV02",
            ho_ten="TS. Phạm Minh Đức",
            email="gv2@vinhuni.edu.vn",
            loai_nguoi_dung="CAN_BO"
        )
        self.user_sv = nguoi_dung.objects.create(
            ma_dinh_danh_cong="211108234",
            ho_ten="Nguyễn Trọng Mạnh",
            email="sv1@vinhuni.edu.vn",
            loai_nguoi_dung="SINH_VIEN"
        )

        self.gv1 = giang_vien.objects.create(
            nguoi_dung=self.user_gv1,
            khoa=self.khoa_cntt,
            bo_mon=self.bo_mon_ktpm,
            ma_can_bo="CB_GV01",
            hoc_vi="TS"
        )
        self.gv2 = giang_vien.objects.create(
            nguoi_dung=self.user_gv2,
            khoa=self.khoa_cntt,
            bo_mon=self.bo_mon_ktpm,
            ma_can_bo="CB_GV02",
            hoc_vi="TS"
        )
        self.sv = sinh_vien.objects.create(
            nguoi_dung=self.user_sv,
            khoa=self.khoa_cntt,
            ma_sinh_vien="211108234",
            lop="62K1-CNTT"
        )

        # 3. Tạo đợt & hồ sơ
        self.dot_obj = dot.objects.create(
            khoa=self.khoa_cntt,
            ma_dot="DOT26_HK2_TEST",
            ten_dot="Đợt Test HK2",
            nam_hoc="2026-2027",
            hoc_ky=2,
            trang_thai=DotTrangThai.CHAM_DIEM,
            nguoi_tao=self.user_dean
        )
        self.hs = ho_so.objects.create(
            dot=self.dot_obj,
            sinh_vien=self.sv,
            trang_thai=HoSoTrangThai.CHO_PHAN_BIEN
        )

        # 4. Tạo bản phân công & gán GV1 làm GVHD
        self.bpc = ban_phan_cong.objects.create(
            dot=self.dot_obj,
            trang_thai=BanPhanCongTrangThai.DA_CONG_BO,
            nguoi_tao=self.user_dean
        )
        self.pchd = phan_cong_huong_dan.objects.create(
            ban_phan_cong=self.bpc,
            ho_so=self.hs,
            giang_vien=self.gv1,
            trang_thai=PhanCongHuongDanTrangThai.DONG_Y
        )

    def test_gvpb_cannot_be_same_as_gvhd(self):
        """Rule GEMINI.md: Giảng viên phản biện không được trùng với GVHD của cùng một hồ sơ"""
        # Thử phân công GV1 (vốn là GVHD của hồ sơ) làm GVPB
        pcc = phan_cong_cham(
            ho_so=self.hs,
            loai=PhanCongChamLoai.PHAN_BIEN,
            giang_vien=self.gv1,  # Trùng GVHD
            nguoi_phan_cong=self.user_dean
        )
        with self.assertRaises(ValidationError):
            pcc.clean()

    def test_gvpb_can_be_different_lecturer(self):
        """Phân công giảng viên khác (GV2) làm phản biện phải hợp lệ"""
        pcc = phan_cong_cham(
            ho_so=self.hs,
            loai=PhanCongChamLoai.PHAN_BIEN,
            giang_vien=self.gv2,  # Khác GVHD
            nguoi_phan_cong=self.user_dean
        )
        try:
            pcc.clean()
        except ValidationError:
            self.fail("Phân công GVPB khác GVHD không được ném ra ValidationError!")

    def test_diem_da_gui_cannot_be_modified_without_reopen(self):
        """Rule GEMINI.md: Điểm đã gửi (DA_GUI) không thể chỉnh sửa nếu không có lệnh mở lại từ Trưởng khoa"""
        diem_obj = diem_thanh_phan.objects.create(
            ho_so=self.hs,
            thanh_phan=ThanhPhanDiem.HUONG_DAN,
            nguoi_cham=self.gv1,
            diem=8.50,
            trang_thai=DiemThanhPhanTrangThai.DA_GUI
        )
        # Thử chỉnh sửa điểm khi trạng thái vẫn đang là DA_GUI
        diem_obj.diem = 9.50
        with self.assertRaises(ValidationError):
            diem_obj.clean()

    def test_diem_thanh_phan_valid_range(self):
        """Điểm số phải nằm trong khoảng từ 0.00 đến 10.00"""
        diem_invalid = diem_thanh_phan(
            ho_so=self.hs,
            thanh_phan=ThanhPhanDiem.HUONG_DAN,
            nguoi_cham=self.gv1,
            diem=11.00,
            trang_thai=DiemThanhPhanTrangThai.NHAP
        )
        with self.assertRaises(ValidationError):
            diem_invalid.clean()
