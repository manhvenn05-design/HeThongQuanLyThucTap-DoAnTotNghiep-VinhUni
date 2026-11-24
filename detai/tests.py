from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from core.constants import (
    DotTrangThai,
    DotLoai,
    HoSoTrangThai,
    DeTaiGoiYTrangThai,
    DeTaiNguon,
    DeTaiTrangThai,
)
from accounts.models import nguoi_dung
from organization.models import khoa, bo_mon, giang_vien, sinh_vien
from dots.models import dot
from hoso.models import ho_so
from detai.models import de_tai_goi_y, de_tai
from hethong.models import thong_bao, nhat_ky_he_thong
from core.state import chuyen_trang_thai_dot
from detai.services.topic_service import (
    TopicValidationError,
    tao_de_tai_goi_y,
    dong_hoac_mo_de_tai_goi_y,
    sinh_vien_chon_de_tai_goi_y,
    sinh_vien_de_xuat_de_tai,
    gvhd_phe_duyet_de_tai,
    gvhd_duyet_hang_loat_de_tai,
)


class Sprint3TopicTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Tạo khoa CNTT & Trưởng khoa
        self.khoa_cntt = khoa.objects.create(
            ma_khoa="CNTT",
            ten_khoa="Khoa Công nghệ Thông tin"
        )
        self.user_tk = nguoi_dung.objects.create(
            ma_dinh_danh_cong="CB_TK01",
            ho_ten="TS. Nguyễn Văn An",
            loai_nguoi_dung="CAN_BO"
        )
        self.gv_tk = giang_vien.objects.create(
            nguoi_dung=self.user_tk,
            ma_can_bo="CB_TK01",
            khoa=self.khoa_cntt,
            hoc_vi="TS"
        )

        # 2. Tạo 2 giảng viên hướng dẫn
        self.bm_ktpm = bo_mon.objects.create(ma_bo_mon="KTPM", ten_bo_mon="Kỹ thuật phần mềm", khoa=self.khoa_cntt)

        self.user_gv1 = nguoi_dung.objects.create(
            ma_dinh_danh_cong="CB_GV01",
            ho_ten="ThS. Trần Văn B",
            loai_nguoi_dung="CAN_BO"
        )
        self.gv1 = giang_vien.objects.create(
            nguoi_dung=self.user_gv1,
            ma_can_bo="CB_GV01",
            khoa=self.khoa_cntt,
            bo_mon=self.bm_ktpm,
            hoc_vi="ThS"
        )

        self.user_gv2 = nguoi_dung.objects.create(
            ma_dinh_danh_cong="CB_GV02",
            ho_ten="ThS. Lê Thị C",
            loai_nguoi_dung="CAN_BO"
        )
        self.gv2 = giang_vien.objects.create(
            nguoi_dung=self.user_gv2,
            ma_can_bo="CB_GV02",
            khoa=self.khoa_cntt,
            bo_mon=self.bm_ktpm,
            hoc_vi="ThS"
        )

        # 3. Tạo đợt ở giai đoạn CHOT_DE_TAI
        self.dot_test = dot.objects.create(
            ma_dot="DOT26_HK2_DETAI",
            ten_dot="Đợt Đồ án Sprint 3",
            khoa=self.khoa_cntt,
            nam_hoc="2025-2026",
            hoc_ky=2,
            loai=DotLoai.DO_AN,
            trang_thai=DotTrangThai.CHOT_DE_TAI,
            so_sv_toi_da_moi_gv=5,
            nguoi_tao=self.user_tk
        )

        # 4. Tạo sinh viên 1 & hồ sơ (được phân công cho gv1, trạng thái CHO_CHOT_DE_TAI)
        self.user_sv1 = nguoi_dung.objects.create(
            ma_dinh_danh_cong="21110001",
            ho_ten="Sinh viên 01",
            loai_nguoi_dung="SINH_VIEN"
        )
        self.sv1 = sinh_vien.objects.create(
            nguoi_dung=self.user_sv1,
            ma_sinh_vien="21110001",
            khoa=self.khoa_cntt,
            lop="62KTPM1"
        )
        self.hs1 = ho_so.objects.create(
            dot=self.dot_test,
            sinh_vien=self.sv1,
            trang_thai=HoSoTrangThai.CHO_CHOT_DE_TAI,
            giang_vien_huong_dan=self.gv1
        )

        # 5. Tạo sinh viên 2 & hồ sơ (được phân công cho gv1)
        self.user_sv2 = nguoi_dung.objects.create(
            ma_dinh_danh_cong="21110002",
            ho_ten="Sinh viên 02",
            loai_nguoi_dung="SINH_VIEN"
        )
        self.sv2 = sinh_vien.objects.create(
            nguoi_dung=self.user_sv2,
            ma_sinh_vien="21110002",
            khoa=self.khoa_cntt,
            lop="62KTPM1"
        )
        self.hs2 = ho_so.objects.create(
            dot=self.dot_test,
            sinh_vien=self.sv2,
            trang_thai=HoSoTrangThai.CHO_CHOT_DE_TAI,
            giang_vien_huong_dan=self.gv1
        )

    # --------------------------------------------------------------------------
    # UC12: ĐỀ TÀI GỢI Ý CỦA GIẢNG VIÊN
    # --------------------------------------------------------------------------
    def test_uc12_tao_de_tai_goi_y_thanh_cong(self):
        topic = tao_de_tai_goi_y(
            dot_obj=self.dot_test,
            giang_vien_obj=self.gv1,
            ten_de_tai="Xây dựng hệ thống quản lý học tập thông minh",
            mo_ta="Sử dụng Django và Tailwind",
            so_luong_toi_da=2,
            nguoi_thuc_hien=self.user_gv1
        )
        self.assertEqual(topic.ten_de_tai, "Xây dựng hệ thống quản lý học tập thông minh")
        self.assertEqual(topic.so_luong_toi_da, 2)
        self.assertEqual(topic.trang_thai, DeTaiGoiYTrangThai.MO)
        self.assertTrue(nhat_ky_he_thong.objects.filter(hanh_dong="TAO_DE_TAI_GOI_Y").exists())

    def test_uc12_tao_de_tai_goi_y_validate_empty_name(self):
        with self.assertRaises(TopicValidationError):
            tao_de_tai_goi_y(
                dot_obj=self.dot_test,
                giang_vien_obj=self.gv1,
                ten_de_tai="   "
            )

    def test_uc12_dong_mo_de_tai_goi_y(self):
        topic = tao_de_tai_goi_y(
            dot_obj=self.dot_test,
            giang_vien_obj=self.gv1,
            ten_de_tai="Đề tài thử nghiệm",
            so_luong_toi_da=1,
            nguoi_thuc_hien=self.user_gv1
        )
        # Đóng
        dong_hoac_mo_de_tai_goi_y(topic, mo_dang_ky=False, nguoi_thuc_hien=self.user_gv1)
        topic.refresh_from_db()
        self.assertEqual(topic.trang_thai, DeTaiGoiYTrangThai.DONG)

        # Mở lại
        dong_hoac_mo_de_tai_goi_y(topic, mo_dang_ky=True, nguoi_thuc_hien=self.user_gv1)
        topic.refresh_from_db()
        self.assertEqual(topic.trang_thai, DeTaiGoiYTrangThai.MO)

    # --------------------------------------------------------------------------
    # UC13: SINH VIÊN CHỌN ĐỀ TÀI GỢI Ý CỦA GVHD
    # --------------------------------------------------------------------------
    def test_uc13_sinh_vien_chon_de_tai_goi_y_thanh_cong(self):
        topic = tao_de_tai_goi_y(
            dot_obj=self.dot_test,
            giang_vien_obj=self.gv1,
            ten_de_tai="Đề tài gợi ý số 1",
            so_luong_toi_da=2,
            nguoi_thuc_hien=self.user_gv1
        )
        dt = sinh_vien_chon_de_tai_goi_y(
            ho_so_obj=self.hs1,
            de_tai_goi_y_obj=topic,
            nguoi_thuc_hien=self.user_sv1
        )
        self.assertEqual(dt.ten_de_tai, "Đề tài gợi ý số 1")
        self.assertEqual(dt.nguon, DeTaiNguon.GV_DUA_RA)
        self.assertEqual(dt.trang_thai, DeTaiTrangThai.CHO_CHOT)
        self.assertEqual(dt.de_tai_goi_y, topic)
        # GVHD nhận được thông báo
        self.assertTrue(thong_bao.objects.filter(nguoi_nhan=self.user_gv1, loai="DANG_KY_DE_TAI").exists())

    def test_uc13_sinh_vien_chon_de_tai_sai_gvhd(self):
        # Đề tài thuộc GV2, nhưng SV1 được phân công cho GV1
        topic_gv2 = tao_de_tai_goi_y(
            dot_obj=self.dot_test,
            giang_vien_obj=self.gv2,
            ten_de_tai="Đề tài của GV2",
            so_luong_toi_da=2
        )
        with self.assertRaises(TopicValidationError) as ctx:
            sinh_vien_chon_de_tai_goi_y(
                ho_so_obj=self.hs1,
                de_tai_goi_y_obj=topic_gv2
            )
        self.assertIn("chỉ được chọn đề tài gợi ý do chính Giảng viên hướng dẫn", str(ctx.exception))

    def test_uc13_sinh_vien_chon_de_tai_da_dong(self):
        topic = tao_de_tai_goi_y(
            dot_obj=self.dot_test,
            giang_vien_obj=self.gv1,
            ten_de_tai="Đề tài đã đóng",
            so_luong_toi_da=1
        )
        dong_hoac_mo_de_tai_goi_y(topic, mo_dang_ky=False)
        with self.assertRaises(TopicValidationError) as ctx:
            sinh_vien_chon_de_tai_goi_y(
                ho_so_obj=self.hs1,
                de_tai_goi_y_obj=topic
            )
        self.assertIn("hiện đang đóng", str(ctx.exception))

    def test_uc13_sinh_vien_chon_de_tai_het_cho(self):
        topic = tao_de_tai_goi_y(
            dot_obj=self.dot_test,
            giang_vien_obj=self.gv1,
            ten_de_tai="Đề tài giới hạn 1 sinh viên",
            so_luong_toi_da=1
        )
        # SV1 chọn trước
        sinh_vien_chon_de_tai_goi_y(ho_so_obj=self.hs1, de_tai_goi_y_obj=topic)
        # SV2 cố tình chọn tiếp -> Lỗi hết chỗ
        with self.assertRaises(TopicValidationError) as ctx:
            sinh_vien_chon_de_tai_goi_y(ho_so_obj=self.hs2, de_tai_goi_y_obj=topic)
        self.assertIn("đã đủ số lượng", str(ctx.exception))

    # --------------------------------------------------------------------------
    # UC14: SINH VIÊN TỰ ĐỀ XUẤT ĐỀ TÀI MỚI
    # --------------------------------------------------------------------------
    def test_uc14_sinh_vien_de_xuat_de_tai_thanh_cong(self):
        dt = sinh_vien_de_xuat_de_tai(
            ho_so_obj=self.hs1,
            ten_de_tai="Nghiên cứu ứng dụng Blockchain trong chứng chỉ giáo dục",
            mo_ta="Sử dụng Solidity và Smart Contract",
            nguoi_thuc_hien=self.user_sv1
        )
        self.assertEqual(dt.ten_de_tai, "Nghiên cứu ứng dụng Blockchain trong chứng chỉ giáo dục")
        self.assertEqual(dt.nguon, DeTaiNguon.SV_DE_XUAT)
        self.assertIsNone(dt.de_tai_goi_y)
        self.assertEqual(dt.trang_thai, DeTaiTrangThai.CHO_CHOT)
        self.assertTrue(thong_bao.objects.filter(nguoi_nhan=self.user_gv1, loai="DE_XUAT_DE_TAI").exists())

    def test_uc14_sinh_vien_de_xuat_de_tai_empty_name(self):
        with self.assertRaises(TopicValidationError):
            sinh_vien_de_xuat_de_tai(
                ho_so_obj=self.hs1,
                ten_de_tai="   "
            )

    # --------------------------------------------------------------------------
    # UC15: GVHD PHÊ DUYỆT ĐỀ TÀI (CHỐT / TRẢ LẠI / DUYỆT HÀNG LOẠT)
    # --------------------------------------------------------------------------
    def test_uc15_gvhd_phe_duyet_chap_nhan(self):
        dt = sinh_vien_de_xuat_de_tai(
            ho_so_obj=self.hs1,
            ten_de_tai="Hệ thống chấm trắc nghiệm bằng thị giác máy tính"
        )
        gvhd_phe_duyet_de_tai(
            de_tai_obj=dt,
            chap_nhan=True,
            nguoi_thuc_hien=self.user_gv1
        )
        dt.refresh_from_db()
        self.hs1.refresh_from_db()

        self.assertEqual(dt.trang_thai, DeTaiTrangThai.DA_CHOT)
        self.assertIsNotNone(dt.ngay_chot)
        # Hồ sơ được gán de_tai_hien_tai
        self.assertEqual(self.hs1.de_tai_hien_tai, dt)
        # Hồ sơ chuyển sang DANG_THUC_HIEN theo single state transition
        self.assertEqual(self.hs1.trang_thai, HoSoTrangThai.DANG_THUC_HIEN)
        # Sinh viên nhận được thông báo
        self.assertTrue(thong_bao.objects.filter(nguoi_nhan=self.user_sv1, loai="DE_TAI_DA_CHOT").exists())

    def test_uc15_gvhd_phe_duyet_tra_lai_thanh_cong(self):
        dt = sinh_vien_de_xuat_de_tai(
            ho_so_obj=self.hs1,
            ten_de_tai="Ứng dụng xem phim trực tuyến"
        )
        gvhd_phe_duyet_de_tai(
            de_tai_obj=dt,
            chap_nhan=False,
            gop_y="Phạm vi quá rộng, em cần tập trung vào giải thuật gợi ý phim Collaborative Filtering.",
            nguoi_thuc_hien=self.user_gv1
        )
        dt.refresh_from_db()
        self.hs1.refresh_from_db()

        self.assertEqual(dt.trang_thai, DeTaiTrangThai.TRA_LAI)
        self.assertIn("Collaborative Filtering", dt.gop_y_cua_gv)
        # Hồ sơ giữ nguyên CHO_CHOT_DE_TAI
        self.assertEqual(self.hs1.trang_thai, HoSoTrangThai.CHO_CHOT_DE_TAI)
        self.assertIsNone(self.hs1.de_tai_hien_tai)
        self.assertTrue(thong_bao.objects.filter(nguoi_nhan=self.user_sv1, loai="DE_TAI_TRA_LAI").exists())

    def test_uc15_gvhd_phe_duyet_tra_lai_khong_co_gop_y(self):
        dt = sinh_vien_de_xuat_de_tai(
            ho_so_obj=self.hs1,
            ten_de_tai="Ứng dụng thương mại điện tử"
        )
        with self.assertRaises(TopicValidationError) as ctx:
            gvhd_phe_duyet_de_tai(
                de_tai_obj=dt,
                chap_nhan=False,
                gop_y="   "
            )
        self.assertIn("Bắt buộc phải nhập ý kiến góp ý", str(ctx.exception))

    def test_uc15_gvhd_duyet_hang_loat(self):
        # SV1 và SV2 cùng đề xuất
        dt1 = sinh_vien_de_xuat_de_tai(ho_so_obj=self.hs1, ten_de_tai="Đề tài 1")
        dt2 = sinh_vien_de_xuat_de_tai(ho_so_obj=self.hs2, ten_de_tai="Đề tài 2")

        count = gvhd_duyet_hang_loat_de_tai(
            danh_sach_de_tai_ids=[dt1.id, dt2.id],
            giang_vien_obj=self.gv1,
            nguoi_thuc_hien=self.user_gv1
        )
        self.assertEqual(count, 2)

        dt1.refresh_from_db()
        dt2.refresh_from_db()
        self.assertEqual(dt1.trang_thai, DeTaiTrangThai.DA_CHOT)
        self.assertEqual(dt2.trang_thai, DeTaiTrangThai.DA_CHOT)

        self.hs1.refresh_from_db()
        self.hs2.refresh_from_db()
        self.assertEqual(self.hs1.trang_thai, HoSoTrangThai.DANG_THUC_HIEN)
        self.assertEqual(self.hs2.trang_thai, HoSoTrangThai.DANG_THUC_HIEN)

    # --------------------------------------------------------------------------
    # VIEWS & ACTIONS TEST
    # --------------------------------------------------------------------------
    def test_sprint3_dashboard_view(self):
        url = reverse("detai:dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Giám sát Tiến độ")

    def test_action_tao_de_tai_goi_y(self):
        url = reverse("detai:tao_de_tai_goi_y")
        response = self.client.post(url, {
            "dot_id": self.dot_test.id,
            "ten_de_tai": "Đề tài tạo từ Form Web",
            "so_luong_toi_da": 2,
            "mo_ta": "Mô tả web"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(de_tai_goi_y.objects.filter(ten_de_tai="Đề tài tạo từ Form Web").exists())

    def test_action_gvhd_phe_duyet_view(self):
        dt = sinh_vien_de_xuat_de_tai(ho_so_obj=self.hs1, ten_de_tai="Đề tài test view")
        url = reverse("detai:gvhd_phe_duyet", kwargs={"de_tai_id": dt.id})
        response = self.client.post(url, {
            "hanh_dong": "CHAP_NHAN"
        })
        self.assertEqual(response.status_code, 302)
        dt.refresh_from_db()
        self.assertEqual(dt.trang_thai, DeTaiTrangThai.DA_CHOT)

    def test_action_chuyen_sang_thuc_hien(self):
        url = reverse("detai:chuyen_sang_thuc_hien", kwargs={"dot_id": self.dot_test.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.dot_test.refresh_from_db()
        self.assertEqual(self.dot_test.trang_thai, DotTrangThai.THUC_HIEN)
