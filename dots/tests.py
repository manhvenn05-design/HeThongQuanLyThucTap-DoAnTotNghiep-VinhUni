from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from core.constants import (
    DotLoai,
    DotTrangThai,
    HinhThucCham,
    ThanhPhanDiem,
)
from accounts.models import nguoi_dung
from organization.models import khoa
from dots.models import dot, dot_trong_so
from dots.services import (
    TrongSoValidationError,
    lay_trong_so_mac_dinh,
    khoi_tao_trong_so_mac_dinh,
    cap_nhat_trong_so_dot,
)
from dots.selectors import get_dot_weights
from hethong.models import nhat_ky_he_thong


class DotWeightConfigurationTestCase(TestCase):
    """
    Kiểm thử toàn diện tính năng Cấu hình phân phối điểm (UC03).
    Bao phủ:
    - Trọng số mặc định theo loại đợt (Đồ án 40-20-40, Thực tập 40-30-30).
    - Validation: Tổng = 100%, không nhận số âm, không sửa đợt đã hoàn tất.
    - Lưu vào CSDL và ghi nhận nhật ký hệ thống (nhat_ky_he_thong).
    - View HTTP request và flash messages.
    """
    def setUp(self):
        self.client = Client()

        # 1. Tạo khoa CNTT
        self.khoa_cntt = khoa.objects.create(
            ma_khoa="CNTT",
            ten_khoa="Khoa Công nghệ Thông tin"
        )

        # 2. Tạo tài khoản Trưởng khoa
        self.user_tk = nguoi_dung.objects.create(
            ma_dinh_danh_cong="CB_TK01",
            ho_ten="TS. Nguyễn Văn An",
            loai_nguoi_dung="CAN_BO"
        )

        # 3. Tạo đợt Đồ án (DO_AN)
        self.dot_do_an = dot.objects.create(
            ma_dot="DOT26_DA_TEST",
            ten_dot="Đợt Đồ án Tốt nghiệp Test",
            khoa=self.khoa_cntt,
            nam_hoc="2025-2026",
            hoc_ky=2,
            loai=DotLoai.DO_AN,
            trang_thai=DotTrangThai.CHUAN_BI,
            so_sv_toi_da_moi_gv=15,
            hinh_thuc_cham=HinhThucCham.HOI_DONG,
            nguoi_tao=self.user_tk
        )

        # 4. Tạo đợt Thực tập (THUC_TAP)
        self.dot_thuc_tap = dot.objects.create(
            ma_dot="DOT26_TT_TEST",
            ten_dot="Đợt Thực tập Tốt nghiệp Test",
            khoa=self.khoa_cntt,
            nam_hoc="2025-2026",
            hoc_ky=2,
            loai=DotLoai.THUC_TAP,
            trang_thai=DotTrangThai.CHUAN_BI,
            so_sv_toi_da_moi_gv=20,
            hinh_thuc_cham=HinhThucCham.PHAN_BIEN,
            nguoi_tao=self.user_tk
        )

    def test_lay_trong_so_mac_dinh_do_an(self):
        """Đồ án mặc định: HUONG_DAN 40%, PHAN_BIEN 20%, HOI_DONG 40% (Tổng = 100%)"""
        ds = lay_trong_so_mac_dinh(DotLoai.DO_AN)
        weights_dict = dict(ds)
        self.assertEqual(weights_dict[ThanhPhanDiem.HUONG_DAN], 40.0)
        self.assertEqual(weights_dict[ThanhPhanDiem.PHAN_BIEN], 20.0)
        self.assertEqual(weights_dict[ThanhPhanDiem.HOI_DONG], 40.0)
        self.assertEqual(sum(weights_dict.values()), 100.0)

    def test_lay_trong_so_mac_dinh_thuc_tap(self):
        """Thực tập mặc định: HUONG_DAN 40%, NOI_THUC_TAP 30%, PHAN_BIEN 30% (Tổng = 100%)"""
        ds = lay_trong_so_mac_dinh(DotLoai.THUC_TAP)
        weights_dict = dict(ds)
        self.assertEqual(weights_dict[ThanhPhanDiem.HUONG_DAN], 40.0)
        self.assertEqual(weights_dict[ThanhPhanDiem.NOI_THUC_TAP], 30.0)
        self.assertEqual(weights_dict[ThanhPhanDiem.PHAN_BIEN], 30.0)
        self.assertEqual(sum(weights_dict.values()), 100.0)

    def test_khoi_tao_trong_so_mac_dinh_cho_dot_moi(self):
        """Tự động khởi tạo cấu hình trọng số mặc định cho đợt khi chưa có"""
        self.assertFalse(dot_trong_so.objects.filter(dot=self.dot_do_an).exists())
        khoi_tao_trong_so_mac_dinh(self.dot_do_an)
        self.assertTrue(dot_trong_so.objects.filter(dot=self.dot_do_an).exists())
        self.assertEqual(dot_trong_so.objects.filter(dot=self.dot_do_an).count(), 3)

    def test_get_dot_weights_selector_auto_init(self):
        """Selector get_dot_weights tự động sinh trọng số nếu đợt chưa có"""
        qs = get_dot_weights(self.dot_thuc_tap)
        self.assertEqual(qs.count(), 3)
        self.assertEqual(dot_trong_so.objects.filter(dot=self.dot_thuc_tap).count(), 3)

    def test_cap_nhat_trong_so_thanh_cong(self):
        """Cập nhật phân bổ trọng số điểm tùy biến hợp lệ (Tổng = 100%)"""
        new_weights = {
            ThanhPhanDiem.HUONG_DAN: 50.0,
            ThanhPhanDiem.NOI_THUC_TAP: 0.0,
            ThanhPhanDiem.PHAN_BIEN: 20.0,
            ThanhPhanDiem.HOI_DONG: 30.0,
        }
        res = cap_nhat_trong_so_dot(
            dot_obj=self.dot_do_an,
            trong_so_dict=new_weights,
            nguoi_thuc_hien=self.user_tk,
            ip_address="127.0.0.1"
        )
        self.assertEqual(len(res), 3) # Chỉ tạo các thành phần > 0
        hd = dot_trong_so.objects.get(dot=self.dot_do_an, thanh_phan=ThanhPhanDiem.HUONG_DAN)
        self.assertEqual(float(hd.trong_so), 50.0)
        
        # Kiểm tra ghi nhật ký hệ thống
        self.assertTrue(
            nhat_ky_he_thong.objects.filter(
                hanh_dong="CAP_NHAT_TRONG_SO_DIEM",
                doi_tuong_id=self.dot_do_an.id
            ).exists()
        )

    def test_cap_nhat_trong_so_that_bai_khi_tong_khac_100(self):
        """Validate chặn khi tổng các trọng số khác 100%"""
        invalid_weights = {
            ThanhPhanDiem.HUONG_DAN: 40.0,
            ThanhPhanDiem.PHAN_BIEN: 20.0,
            ThanhPhanDiem.HOI_DONG: 30.0, # Tổng = 90%
        }
        with self.assertRaises(TrongSoValidationError) as ctx:
            cap_nhat_trong_so_dot(
                dot_obj=self.dot_do_an,
                trong_so_dict=invalid_weights,
                nguoi_thuc_hien=self.user_tk
            )
        self.assertIn("phải bằng đúng 100%", str(ctx.exception))

    def test_cap_nhat_trong_so_that_bai_khi_co_so_am(self):
        """Validate chặn khi có trọng số âm"""
        negative_weights = {
            ThanhPhanDiem.HUONG_DAN: -10.0,
            ThanhPhanDiem.PHAN_BIEN: 50.0,
            ThanhPhanDiem.HOI_DONG: 60.0,
        }
        with self.assertRaises(TrongSoValidationError) as ctx:
            cap_nhat_trong_so_dot(
                dot_obj=self.dot_do_an,
                trong_so_dict=negative_weights,
                nguoi_thuc_hien=self.user_tk
            )
        self.assertIn("không được là số âm", str(ctx.exception))

    def test_cap_nhat_trong_so_that_bai_khi_dot_da_hoan_tat(self):
        """Không cho phép sửa cấu hình điểm của đợt đã HOAN_TAT"""
        self.dot_do_an.trang_thai = DotTrangThai.HOAN_TAT
        self.dot_do_an.save(update_fields=['trang_thai'])

        weights = {
            ThanhPhanDiem.HUONG_DAN: 40.0,
            ThanhPhanDiem.PHAN_BIEN: 20.0,
            ThanhPhanDiem.HOI_DONG: 40.0,
        }
        with self.assertRaises(TrongSoValidationError) as ctx:
            cap_nhat_trong_so_dot(
                dot_obj=self.dot_do_an,
                trong_so_dict=weights,
                nguoi_thuc_hien=self.user_tk
            )
        self.assertIn("đã hoàn tất", str(ctx.exception))

    def test_view_update_dot_weights_post_thanh_cong(self):
        """Test HTTP POST endpoint lưu trọng số thành công và chuyển hướng"""
        url = reverse("update_dot_weights", kwargs={"dot_id": self.dot_do_an.id})
        response = self.client.post(url, {
            "weight_HUONG_DAN": "45",
            "weight_NOI_THUC_TAP": "0",
            "weight_PHAN_BIEN": "15",
            "weight_HOI_DONG": "40",
        })
        self.assertEqual(response.status_code, 302)
        hd = dot_trong_so.objects.get(dot=self.dot_do_an, thanh_phan=ThanhPhanDiem.HUONG_DAN)
        self.assertEqual(float(hd.trong_so), 45.0)

    def test_view_update_dot_weights_post_sai_tong_khong_crash(self):
        """Test HTTP POST endpoint với tổng != 100% xử lý an toàn, thông báo lỗi qua message"""
        url = reverse("update_dot_weights", kwargs={"dot_id": self.dot_do_an.id})
        response = self.client.post(url, {
            "weight_HUONG_DAN": "50",
            "weight_NOI_THUC_TAP": "0",
            "weight_PHAN_BIEN": "50",
            "weight_HOI_DONG": "20", # Tổng 120%
        })
        self.assertEqual(response.status_code, 302)
