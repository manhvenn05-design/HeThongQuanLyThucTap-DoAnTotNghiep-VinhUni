"""
Tầng Services cho app dots (Quản lý Đợt - UC03).
Chứa toàn bộ logic nghiệp vụ mở đợt, sinh mốc thời gian theo preset (15 tuần, 10 tuần, 8 tuần, tùy chỉnh)
và cấu hình trọng số điểm theo quy chế.
"""
from datetime import timedelta
from typing import Optional, List, Dict, Tuple
from django.db import transaction
from django.utils import timezone
from dots.models import dot, dot_moc_thoi_gian, dot_trong_so
from core.constants import (
    DotLoai,
    DotTrangThai,
    HinhThucCham,
    LoaiMocThoiGian,
    ThanhPhanDiem,
)
from hethong.models import nhat_ky_he_thong


PRESETS_CONFIG = {
    "DO_AN_15_TUAN": {
        "ten": "Đồ án tốt nghiệp chính quy (15 tuần)",
        "so_tuan": 15,
        "loai": DotLoai.DO_AN,
        "hinh_thuc": HinhThucCham.HOI_DONG,
        "mocs": [
            ("MOC_DANG_KY", "Đăng ký nguyện vọng & Chốt danh sách", LoaiMocThoiGian.PHAN_CONG, 2),
            ("MOC_CHOT_DE_TAI", "Thống nhất & Chốt đề tài với GVHD", LoaiMocThoiGian.CHOT_DE_TAI, 4),
            ("MOC_BC_TIEN_DO_1", "Báo cáo tiến độ đợt 1 (30% khối lượng)", LoaiMocThoiGian.NOP_TIEN_DO, 7),
            ("MOC_BC_TIEN_DO_2", "Báo cáo tiến độ đợt 2 (70% khối lượng)", LoaiMocThoiGian.NOP_TIEN_DO, 11),
            ("MOC_NOP_TOAN_VAN", "Nộp quyển báo cáo toàn văn & Source code", LoaiMocThoiGian.NOP_BAO_CAO, 14),
            ("MOC_CHAM_PB_HD", "Chấm phản biện & Bảo vệ trước Hội đồng", LoaiMocThoiGian.CHAM_DIEM, 15),
        ],
        "trong_so": [
            (ThanhPhanDiem.HUONG_DAN, 30),
            (ThanhPhanDiem.PHAN_BIEN, 20),
            (ThanhPhanDiem.HOI_DONG, 50),
        ]
    },
    "THUC_TAP_10_TUAN": {
        "ten": "Thực tập tốt nghiệp doanh nghiệp (10 tuần)",
        "so_tuan": 10,
        "loai": DotLoai.THUC_TAP,
        "hinh_thuc": HinhThucCham.PHAN_BIEN,
        "mocs": [
            ("MOC_TIEP_NHAN", "Xác nhận đơn vị thực tập doanh nghiệp", LoaiMocThoiGian.PHAN_CONG, 2),
            ("MOC_BC_GIUA_DOT", "Báo cáo tiến độ giữa đợt tại doanh nghiệp", LoaiMocThoiGian.NOP_TIEN_DO, 5),
            ("MOC_NOP_NHAT_KY", "Nộp nhật ký thực tập & Giấy xác nhận DN", LoaiMocThoiGian.NOP_BAO_CAO, 9),
            ("MOC_CHAM_DIEM_TT", "Đánh giá GVHD & Đơn vị thực tập", LoaiMocThoiGian.CHAM_DIEM, 10),
        ],
        "trong_so": [
            (ThanhPhanDiem.HUONG_DAN, 40),
            (ThanhPhanDiem.NOI_THUC_TAP, 40),
            (ThanhPhanDiem.PHAN_BIEN, 20),
        ]
    },
    "HE_RUT_GON_8_TUAN": {
        "ten": "Học kỳ hè rút gọn (8 tuần)",
        "so_tuan": 8,
        "loai": DotLoai.THUC_TAP,
        "hinh_thuc": HinhThucCham.PHAN_BIEN,
        "mocs": [
            ("MOC_DANG_KY_HE", "Đăng ký đơn vị & Bắt đầu thực tập hè", LoaiMocThoiGian.PHAN_CONG, 1),
            ("MOC_BC_TIEN_DO", "Báo cáo tiến độ tuần 4", LoaiMocThoiGian.NOP_TIEN_DO, 4),
            ("MOC_NOP_MINH_CHUNG", "Nộp minh chứng & Báo cáo hoàn thành", LoaiMocThoiGian.NOP_BAO_CAO, 7),
            ("MOC_TONG_KET", "Tổng kết đánh giá điểm thực tập hè", LoaiMocThoiGian.CHAM_DIEM, 8),
        ],
        "trong_so": [
            (ThanhPhanDiem.HUONG_DAN, 50),
            (ThanhPhanDiem.NOI_THUC_TAP, 50),
        ]
    }
}


@transaction.atomic
def cap_nhat_cau_hinh_dot_preset(
    dot_obj: dot,
    preset_key: str,
    ngay_bat_dau: timezone.datetime,
    tong_so_tuan: int,
    nguoi_thuc_hien,
    ip_address: Optional[str] = None
) -> Tuple[dot, str, int]:
    """
    Cập nhật lại toàn bộ mốc thời gian và trọng số của đợt theo Preset được chọn (UC03).
    Chỉ áp dụng khi đợt đang ở giai đoạn CHUAN_BI.
    """
    # 1. Xóa mốc thời gian và trọng số cũ
    dot_obj.cac_moc_thoi_gian.all().delete()
    dot_obj.cac_trong_so.all().delete()

    if not ngay_bat_dau:
        ngay_bat_dau = timezone.now()

    # 2. Sinh mốc mới theo Preset hoặc Tùy chỉnh
    if preset_key in PRESETS_CONFIG:
        config = PRESETS_CONFIG[preset_key]
        so_tuan_that = config["so_tuan"]
        ten_preset = config["ten"]
        dot_obj.loai = config["loai"]
        dot_obj.hinh_thuc_cham = config["hinh_thuc"]

        for idx, (ma_moc, ten_moc, loai_moc, tuan) in enumerate(config["mocs"], start=1):
            han = ngay_bat_dau + timedelta(weeks=tuan)
            dot_moc_thoi_gian.objects.create(
                dot=dot_obj,
                ma_moc=ma_moc,
                ten_moc=ten_moc,
                loai_moc=loai_moc,
                thu_tu=idx,
                han_cuoi=han
            )

        for thanh_phan, ty_le in config["trong_so"]:
            dot_trong_so.objects.create(
                dot=dot_obj,
                thanh_phan=thanh_phan,
                trong_so=ty_le
            )
    else:
        # Tùy chỉnh số tuần
        so_tuan_that = max(4, min(24, tong_so_tuan))
        ten_preset = f"Tùy chỉnh linh hoạt ({so_tuan_that} tuần)"
        
        custom_mocs = [
            ("MOC_01_KHOI_DONG", "Khởi động & Chốt danh sách", LoaiMocThoiGian.PHAN_CONG, 2),
            ("MOC_02_GIUA_KY", "Báo cáo tiến độ giữa kỳ", LoaiMocThoiGian.NOP_TIEN_DO, max(2, so_tuan_that // 2)),
            ("MOC_03_NOP_BAO_CAO", "Nộp báo cáo và minh chứng", LoaiMocThoiGian.NOP_BAO_CAO, max(1, so_tuan_that - 1)),
            ("MOC_04_TONG_KET", "Đánh giá & Tổng kết điểm", LoaiMocThoiGian.CHAM_DIEM, so_tuan_that),
        ]
        for idx, (ma_moc, ten_moc, loai_moc, tuan) in enumerate(custom_mocs, start=1):
            han = ngay_bat_dau + timedelta(weeks=tuan)
            dot_moc_thoi_gian.objects.create(
                dot=dot_obj,
                ma_moc=ma_moc,
                ten_moc=ten_moc,
                loai_moc=loai_moc,
                thu_tu=idx,
                han_cuoi=han
            )

        dot_trong_so.objects.create(dot=dot_obj, thanh_phan=ThanhPhanDiem.HUONG_DAN, trong_so=50)
        dot_trong_so.objects.create(dot=dot_obj, thanh_phan=ThanhPhanDiem.PHAN_BIEN, trong_so=50)

    dot_obj.save()

    # 3. Ghi nhật ký hệ thống
    nhat_ky_he_thong.objects.create(
        nguoi_thuc_hien=nguoi_thuc_hien,
        hanh_dong="CAP_NHAT_CAU_HINH_DOT",
        doi_tuong_loai="dot",
        doi_tuong_id=dot_obj.id,
        mo_ta=f"Cập nhật cấu hình đợt sang: {ten_preset}. Thời lượng {so_tuan_that} tuần.",
        dia_chi_ip=ip_address,
        thoi_gian=timezone.now(),
    )

    return dot_obj, ten_preset, so_tuan_that


@transaction.atomic
def tao_dot_chuyen_nghiep(
    ma_dot: str,
    ten_dot: str,
    loai: str,
    hoc_ky: int,
    nam_hoc: str,
    khoa,
    nguoi_tao,
    preset_key: Optional[str] = None,
    ngay_bat_dau: Optional[timezone.datetime] = None,
    tong_so_tuan: int = 15,
    so_sv_toi_da_moi_gv: int = 15,
    hinh_thuc_cham: str = HinhThucCham.HOI_DONG,
    ip_address: Optional[str] = None,
) -> dot:
    """
    Dịch vụ tạo mới đợt và tự động sinh các mốc thời gian trải đều theo tuần (UC03).
    """
    dot_obj = dot.objects.create(
        ma_dot=ma_dot.strip().upper(),
        ten_dot=ten_dot.strip(),
        loai=loai,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc.strip(),
        khoa=khoa,
        trang_thai=DotTrangThai.CHUAN_BI,
        so_sv_toi_da_moi_gv=so_sv_toi_da_moi_gv,
        hinh_thuc_cham=hinh_thuc_cham,
        nguoi_tao=nguoi_tao,
    )

    cap_nhat_cau_hinh_dot_preset(
        dot_obj=dot_obj,
        preset_key=preset_key or "DO_AN_15_TUAN",
        ngay_bat_dau=ngay_bat_dau or timezone.now(),
        tong_so_tuan=tong_so_tuan,
        nguoi_thuc_hien=nguoi_tao,
        ip_address=ip_address
    )

    return dot_obj
