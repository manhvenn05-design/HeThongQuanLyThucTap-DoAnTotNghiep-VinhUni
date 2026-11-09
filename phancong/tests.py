from django.test import TestCase, Client
from django.urls import reverse
from core.constants import DotTrangThai, DotLoai, HoSoTrangThai, BanPhanCongTrangThai, PhanCongHuongDanTrangThai
from accounts.models import nguoi_dung
from organization.models import khoa, bo_mon, giang_vien, sinh_vien
from dots.models import dot
from hoso.models import ho_so, diem_dau_vao
from phancong.models import ban_phan_cong, phan_cong_huong_dan
from hethong.models import nhat_ky_he_thong, thong_bao
from core.state import chuyen_trang_thai_dot


class Sprint2PhanCongTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Tạo khoa & Trưởng khoa
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

        # 2. Tạo 4 giảng viên
        self.bm_ktpm = bo_mon.objects.create(ma_bo_mon="KTPM", ten_bo_mon="Kỹ thuật phần mềm", khoa=self.khoa_cntt)
        self.ds_gv = []
        for i in range(1, 5):
            u = nguoi_dung.objects.create(
                ma_dinh_danh_cong=f"CB_GV0{i}",
                ho_ten=f"Giảng viên {i}",
                loai_nguoi_dung="CAN_BO"
            )
            gv = giang_vien.objects.create(
                nguoi_dung=u,
                ma_can_bo=f"CB_GV0{i}",
                khoa=self.khoa_cntt,
                bo_mon=self.bm_ktpm,
                hoc_vi="ThS"
            )
            self.ds_gv.append(gv)

        # 3. Tạo đợt ở giai đoạn PHAN_CONG (Tối đa 5 SV/GV)
        self.dot_test = dot.objects.create(
            ma_dot="DOT26_HK2_TEST",
            ten_dot="Đợt Đồ án Test 2026",
            khoa=self.khoa_cntt,
            nam_hoc="2025-2026",
            hoc_ky=2,
            loai=DotLoai.DO_AN,
            trang_thai=DotTrangThai.CHUAN_BI,
            so_sv_toi_da_moi_gv=5,
            nguoi_tao=self.user_tk
        )

        # 4. Tạo 20 sinh viên & hồ sơ (16 có điểm GPA, 4 chưa có điểm)
        for i in range(1, 21):
            u_sv = nguoi_dung.objects.create(
                ma_dinh_danh_cong=f"211100{i:02d}",
                ho_ten=f"Sinh viên {i:02d}",
                loai_nguoi_dung="SINH_VIEN"
            )
            sv = sinh_vien.objects.create(
                nguoi_dung=u_sv,
                ma_sinh_vien=f"211100{i:02d}",
                khoa=self.khoa_cntt
            )
            hs = ho_so.objects.create(
                dot=self.dot_test,
                sinh_vien=sv,
                trang_thai=HoSoTrangThai.TRONG_DANH_SACH
            )
            if i <= 16:
                # Điểm giảm dần từ 3.9 xuống 2.4
                gpa = round(3.9 - (i - 1) * 0.1, 2)
                diem_dau_vao.objects.create(
                    ho_so=hs,
                    diem_tb_he4=gpa,
                    tin_chi_tich_luy=120 - i
                )

        # Chuyển đợt sang giai đoạn PHAN_CONG
        chuyen_trang_thai_dot(
            dot_obj=self.dot_test,
            trang_thai_moi=DotTrangThai.PHAN_CONG,
            nguoi_thuc_hien=self.user_tk,
            ly_do="Bắt đầu phân công"
        )

    def test_sprint2_dashboard_renders(self):
        """Kiểm tra màn hình Dashboard Sprint 2 hiển thị thành công (HTTP 200)"""
        url = reverse("phancong:dashboard_dot", kwargs={"dot_id": self.dot_test.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Phân công Hướng dẫn Đồ án")
        self.assertContains(response, "cân bằng GPA")
        self.assertContains(response, "Sinh viên chưa phân công giảng viên hướng dẫn")

    def test_snake_draft_allocation_balance(self):
        """Kiểm tra thuật toán Snake-draft chia đều 20 sinh viên cho 5 GV trong khoa (mỗi GV đúng 4 SV) (UC07)"""
        url = reverse("phancong:chay_snake_draft", kwargs={"dot_id": self.dot_test.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Kiểm tra bảng phan_cong_huong_dan
        bpc = ban_phan_cong.objects.filter(dot=self.dot_test).first()
        self.assertIsNotNone(bpc)
        self.assertEqual(bpc.trang_thai, BanPhanCongTrangThai.NHAP)

        dong_qs = phan_cong_huong_dan.objects.filter(ban_phan_cong=bpc)
        self.assertEqual(dong_qs.count(), 20)

        # 5 giảng viên nhận đúng 4 sinh viên mỗi người (20 / 5 = 4)
        tat_ca_gv = giang_vien.objects.filter(khoa=self.khoa_cntt)
        for gv in tat_ca_gv:
            cnt = dong_qs.filter(giang_vien=gv).count()
            self.assertEqual(cnt, 4, f"Giảng viên {gv.nguoi_dung.ho_ten} nhận {cnt} SV, không bằng 4!")

    def test_export_draft_excel(self):
        """Kiểm tra xuất file Excel dự thảo phân công (UC08)"""
        # Chạy phân công trước
        self.client.post(reverse("phancong:chay_snake_draft", kwargs={"dot_id": self.dot_test.id}))

        url = reverse("phancong:xuat_excel", kwargs={"dot_id": self.dot_test.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.assertIn("Du_thao_phan_cong", response["Content-Disposition"])

    def test_send_draft_to_lecturers(self):
        """Kiểm tra Trưởng khoa gửi bản phân công cho GVHD xác nhận (UC07)"""
        # Chạy phân công
        self.client.post(reverse("phancong:chay_snake_draft", kwargs={"dot_id": self.dot_test.id}))

        # Gửi
        url = reverse("phancong:gui_ban_phan_cong", kwargs={"dot_id": self.dot_test.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)

        bpc = ban_phan_cong.objects.get(dot=self.dot_test)
        self.assertEqual(bpc.trang_thai, BanPhanCongTrangThai.DA_GUI)

        # Toàn bộ hồ sơ chuyển sang CHO_XAC_NHAN
        hs_chua_xac_nhan = ho_so.objects.filter(dot=self.dot_test, trang_thai=HoSoTrangThai.CHO_XAC_NHAN).count()
        self.assertEqual(hs_chua_xac_nhan, 20)

        # Kiểm tra thông báo được gửi đến các GV
        self.assertTrue(thong_bao.objects.filter(loai="PHAN_CONG").exists())

    def test_lecturer_review_and_accept_all(self):
        """Kiểm tra Giảng viên xem danh sách và bấm Đồng ý tất cả (UC10)"""
        # Setup: Phân công và gửi
        self.client.post(reverse("phancong:chay_snake_draft", kwargs={"dot_id": self.dot_test.id}))
        self.client.post(reverse("phancong:gui_ban_phan_cong", kwargs={"dot_id": self.dot_test.id}))

        gv_1 = self.ds_gv[0]
        # Xem màn hình xác nhận
        url_view = reverse("phancong:xac_nhan_giang_vien_dot", kwargs={"gv_id": gv_1.id, "dot_id": self.dot_test.id})
        resp = self.client.get(url_view)
        self.assertEqual(resp.status_code, 200)
        # BẢO MẬT: Kiểm tra không chứa nhãn GPA trên trang giảng viên
        self.assertNotContains(resp, "GPA: 3.")

        # Đồng ý tất cả
        url_accept = reverse("phancong:gv_dong_y_tat_ca", kwargs={"gv_id": gv_1.id, "dot_id": self.dot_test.id})
        resp_post = self.client.post(url_accept, follow=True)
        self.assertEqual(resp_post.status_code, 200)

        dong_y_cnt = phan_cong_huong_dan.objects.filter(giang_vien=gv_1, trang_thai=PhanCongHuongDanTrangThai.DONG_Y).count()
        self.assertEqual(dong_y_cnt, 4)

    def test_lecturer_reject_student_with_reason(self):
        """Kiểm tra Giảng viên từ chối sinh viên kèm lý do -> hồ sơ quay về TRONG_DANH_SACH (UC10)"""
        # Setup: Phân công và gửi
        self.client.post(reverse("phancong:chay_snake_draft", kwargs={"dot_id": self.dot_test.id}))
        self.client.post(reverse("phancong:gui_ban_phan_cong", kwargs={"dot_id": self.dot_test.id}))

        gv_1 = self.ds_gv[0]
        pc = phan_cong_huong_dan.objects.filter(giang_vien=gv_1).first()
        hs = pc.ho_so

        # Từ chối kèm lý do
        url_reject = reverse("phancong:gv_phan_hoi_don_le", kwargs={"gv_id": gv_1.id, "pc_id": pc.id})
        resp = self.client.post(url_reject, {
            "hanh_dong": "TU_CHOI",
            "ly_do": "Lệch định hướng nghiên cứu chuyên sâu về Big Data."
        }, follow=True)
        self.assertEqual(resp.status_code, 200)

        # Cập nhật
        pc.refresh_from_db()
        self.assertEqual(pc.trang_thai, PhanCongHuongDanTrangThai.TU_CHOI)
        self.assertEqual(pc.ly_do_tu_choi, "Lệch định hướng nghiên cứu chuyên sâu về Big Data.")

        # Hồ sơ quay về TRONG_DANH_SACH
        hs.refresh_from_db()
        self.assertEqual(hs.trang_thai, HoSoTrangThai.TRONG_DANH_SACH)

    def test_publish_official_assignments_advances_to_sprint3(self):
        """Kiểm tra khi 100% sinh viên được đồng ý -> Công bố chính thức -> chuyển đợt sang CHOT_DE_TAI (Sprint 3) (UC09)"""
        # Setup: Phân công và gửi
        self.client.post(reverse("phancong:chay_snake_draft", kwargs={"dot_id": self.dot_test.id}))
        self.client.post(reverse("phancong:gui_ban_phan_cong", kwargs={"dot_id": self.dot_test.id}))

        # Cho toàn bộ GV trong khoa đồng ý tất cả
        tat_ca_gv = giang_vien.objects.filter(khoa=self.khoa_cntt)
        for gv in tat_ca_gv:
            self.client.post(reverse("phancong:gv_dong_y_tat_ca", kwargs={"gv_id": gv.id, "dot_id": self.dot_test.id}))

        # Trưởng khoa công bố
        url_publish = reverse("phancong:cong_bo_chinh_thuc", kwargs={"dot_id": self.dot_test.id})
        resp = self.client.post(url_publish, follow=True)
        self.assertEqual(resp.status_code, 200)

        # Bản phân công sang DA_CONG_BO
        bpc = ban_phan_cong.objects.get(dot=self.dot_test)
        self.assertEqual(bpc.trang_thai, BanPhanCongTrangThai.DA_CONG_BO)

        # Đợt sang CHOT_DE_TAI (Sprint 3)
        self.dot_test.refresh_from_db()
        self.assertEqual(self.dot_test.trang_thai, DotTrangThai.CHOT_DE_TAI)

        # Hồ sơ có GVHD chính thức và sang CHO_CHOT_DE_TAI
        for hs in ho_so.objects.filter(dot=self.dot_test):
            self.assertIsNotNone(hs.giang_vien_huong_dan)
            self.assertEqual(hs.trang_thai, HoSoTrangThai.CHO_CHOT_DE_TAI)
