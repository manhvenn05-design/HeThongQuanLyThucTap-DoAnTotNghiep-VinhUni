from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from core.constants import (
    MaVaiTro,
    LoaiNguoiDung,
    NguoiDungTrangThai,
    DotLoai,
    DotTrangThai,
    HinhThucCham,
    LoaiMocThoiGian,
    ThanhPhanDiem,
)
from accounts.models import nguoi_dung, vai_tro, nguoi_dung_vai_tro
from organization.models import khoa, bo_mon, giang_vien
from dots.models import dot, dot_moc_thoi_gian, dot_trong_so

class Command(BaseCommand):
    help = "Khởi tạo dữ liệu nền tảng ban đầu (Khoa, Bộ môn, Vai trò, Trưởng khoa, Giảng viên, Đợt mẫu)"

    def handle(self, *args, **options):
        # 1. Superuser Django Admin
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@vinhuni.edu.vn", "admin123456")
            self.stdout.write("[OK] Created Superuser: admin / admin123456")

        # 2. Danh mục Vai trò
        vai_tro_list = [
            (MaVaiTro.TRUONG_KHOA, "Trưởng khoa", "Trưởng khoa quản lý điều phối các đợt thực tập/đồ án của khoa"),
            (MaVaiTro.GIANG_VIEN, "Giảng viên", "Giảng viên hướng dẫn, phản biện hoặc hội đồng"),
            (MaVaiTro.QUAN_TRI, "Quản trị viên", "Cán bộ quản trị kỹ thuật hệ thống"),
        ]
        roles = {}
        for ma, ten, mo_ta in vai_tro_list:
            r, _ = vai_tro.objects.get_or_create(ma_vai_tro=ma, defaults={"ten_vai_tro": ten, "mo_ta": mo_ta})
            roles[ma] = r
        self.stdout.write("[OK] Created 3 system roles")

        # 3. Khoa CNTT
        khoa_cntt, _ = khoa.objects.get_or_create(
            ma_khoa="CNTT",
            defaults={"ten_khoa": "Khoa Công nghệ Thông tin", "dang_hoat_dong": True}
        )
        self.stdout.write(f"[OK] Created faculty: {khoa_cntt.ma_khoa}")

        # 4. Các bộ môn thuộc khoa
        bm_ktpm, _ = bo_mon.objects.get_or_create(khoa=khoa_cntt, ma_bo_mon="KTPM", defaults={"ten_bo_mon": "Kỹ thuật phần mềm"})
        bm_httt, _ = bo_mon.objects.get_or_create(khoa=khoa_cntt, ma_bo_mon="HTTT", defaults={"ten_bo_mon": "Hệ thống thông tin"})
        bm_mmt, _ = bo_mon.objects.get_or_create(khoa=khoa_cntt, ma_bo_mon="MMT", defaults={"ten_bo_mon": "Mạng máy tính & Truyền thông"})
        self.stdout.write("[OK] Created departments: KTPM, HTTT, MMT")

        # 5. Tài khoản Trưởng khoa
        nd_tkhoa, _ = nguoi_dung.objects.get_or_create(
            ma_dinh_danh_cong="CB_TK01",
            defaults={
                "ho_ten": "TS. Nguyễn Văn An",
                "email": "tkhoa_cntt@vinhuni.edu.vn",
                "so_dien_thoai": "0912345678",
                "loai_nguoi_dung": LoaiNguoiDung.GIANG_VIEN,
                "trang_thai": NguoiDungTrangThai.HOAT_DONG,
            }
        )
        gv_tkhoa, _ = giang_vien.objects.get_or_create(
            nguoi_dung=nd_tkhoa,
            defaults={
                "ma_can_bo": "CB_TK01",
                "khoa": khoa_cntt,
                "bo_mon": bm_ktpm,
                "hoc_vi": "TS",
            }
        )
        nguoi_dung_vai_tro.objects.get_or_create(
            nguoi_dung=nd_tkhoa,
            vai_tro=roles[MaVaiTro.TRUONG_KHOA],
            khoa=khoa_cntt,
            defaults={"hieu_luc_tu": timezone.now().date()}
        )
        self.stdout.write(f"[OK] Created Dean: {nd_tkhoa.ma_dinh_danh_cong}")

        # 6. Giảng viên mẫu
        danh_sach_gv = [
            ("CB_GV01", "ThS. Trần Thị Bình", "binhtt@vinhuni.edu.vn", "ThS", bm_ktpm),
            ("CB_GV02", "ThS. Lê Quốc Cường", "cuonglq@vinhuni.edu.vn", "ThS", bm_httt),
            ("CB_GV03", "TS. Phạm Minh Đức", "ducpm@vinhuni.edu.vn", "TS", bm_ktpm),
            ("CB_GV04", "ThS. Hoàng Thị Dung", "dunght@vinhuni.edu.vn", "ThS", bm_mmt),
        ]
        for ma_cb, ho_ten, email, hoc_vi, bm in danh_sach_gv:
            nd, _ = nguoi_dung.objects.get_or_create(
                ma_dinh_danh_cong=ma_cb,
                defaults={
                    "ho_ten": ho_ten,
                    "email": email,
                    "loai_nguoi_dung": LoaiNguoiDung.GIANG_VIEN,
                    "trang_thai": NguoiDungTrangThai.HOAT_DONG,
                }
            )
            giang_vien.objects.get_or_create(
                nguoi_dung=nd,
                defaults={"ma_can_bo": ma_cb, "khoa": khoa_cntt, "bo_mon": bm, "hoc_vi": hoc_vi}
            )
            nguoi_dung_vai_tro.objects.get_or_create(
                nguoi_dung=nd,
                vai_tro=roles[MaVaiTro.GIANG_VIEN],
                khoa=khoa_cntt,
                defaults={"hieu_luc_tu": timezone.now().date()}
            )
        self.stdout.write("[OK] Created 4 sample lecturers")

        # 7. Đợt mẫu ở giai đoạn CHUAN_BI (Sprint 1)
        dot_mau, created = dot.objects.get_or_create(
            ma_dot="DOT26_HK2_CNTT_01",
            defaults={
                "ten_dot": "Thực tập tốt nghiệp HK2 (2026 - 2027)",
                "loai": DotLoai.THUC_TAP,
                "hoc_ky": 2,
                "nam_hoc": "2026-2027",
                "khoa": khoa_cntt,
                "trang_thai": DotTrangThai.CHUAN_BI,
                "so_sv_toi_da_moi_gv": 15,
                "hinh_thuc_cham": HinhThucCham.PHAN_BIEN,
                "nguoi_tao": nd_tkhoa,
            }
        )
        if created:
            now = timezone.now()
            # Mốc thời gian
            mocs = [
                ("MOC_PHAN_CONG", "Hạn phân công GVHD", LoaiMocThoiGian.PHAN_CONG, 1, now + timedelta(days=7)),
                ("MOC_CHOT_DE_TAI", "Hạn chốt đề tài thực tập", LoaiMocThoiGian.CHOT_DE_TAI, 2, now + timedelta(days=14)),
                ("MOC_TIEN_DO_1", "Hạn nộp minh chứng đợt 1", LoaiMocThoiGian.NOP_TIEN_DO, 3, now + timedelta(days=30)),
                ("MOC_TIEN_DO_2", "Hạn nộp minh chứng đợt 2", LoaiMocThoiGian.NOP_TIEN_DO, 4, now + timedelta(days=50)),
                ("MOC_BAO_CAO_CUOI", "Hạn nộp báo cáo cuối đợt", LoaiMocThoiGian.NOP_BAO_CAO, 5, now + timedelta(days=70)),
                ("MOC_CHAM_DIEM", "Hạn hoàn tất chấm điểm", LoaiMocThoiGian.CHAM_DIEM, 6, now + timedelta(days=80)),
            ]
            for ma, ten, loai_moc, thu_tu, han in mocs:
                dot_moc_thoi_gian.objects.create(dot=dot_mau, ma_moc=ma, ten_moc=ten, loai_moc=loai_moc, thu_tu=thu_tu, han_cuoi=han)

            # Trọng số điểm mẫu
            dot_trong_so.objects.create(dot=dot_mau, thanh_phan=ThanhPhanDiem.HUONG_DAN, trong_so=50)
            dot_trong_so.objects.create(dot=dot_mau, thanh_phan=ThanhPhanDiem.NOI_THUC_TAP, trong_so=30)
            dot_trong_so.objects.create(dot=dot_mau, thanh_phan=ThanhPhanDiem.PHAN_BIEN, trong_so=20)

            self.stdout.write(f"[OK] Created sample batch: {dot_mau.ma_dot}")

        self.stdout.write("[SUCCESS] Seed data completed successfully!")
