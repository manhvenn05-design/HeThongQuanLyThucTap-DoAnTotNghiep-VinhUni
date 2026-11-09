"""
Dịch vụ chuyển trạng thái tập trung duy nhất (Single State Transition Service).
Tuân thủ tuyệt đối quy tắc nghiệp vụ mục 5 và mục 7 trong PROJECT_SPEC.
Mọi thay đổi trạng thái của `dot` và `ho_so` bắt buộc phải gọi qua module này.
"""
from django.db import transaction
from django.utils import timezone
from core.constants import DotTrangThai, HoSoTrangThai, BanPhanCongTrangThai
from hethong.models import nhat_ky_he_thong


class StateTransitionError(Exception):
    """Lỗi khi vi phạm điều kiện chuyển trạng thái"""
    pass


@transaction.atomic
def chuyen_trang_thai_dot(dot_obj, trang_thai_moi, nguoi_thuc_hien, ly_do="", ip_address=None):
    """
    Chuyển trạng thái của một đợt thực tập / đồ án.
    Kiểm tra tiền điều kiện chặt chẽ và tự động ghi log vào nhat_ky_he_thong.
    """
    trang_thai_cu = dot_obj.trang_thai
    if trang_thai_cu == trang_thai_moi:
        return dot_obj

    # 1. Kiểm tra thứ tự vòng đời hợp lệ
    hop_le = False
    if trang_thai_cu == DotTrangThai.CHUAN_BI and trang_thai_moi == DotTrangThai.PHAN_CONG:
        # Điều kiện: Phải có ít nhất 1 hồ sơ đã được xác nhận trong đợt
        from hoso.models import ho_so
        if not ho_so.objects.filter(dot=dot_obj).exists():
            raise StateTransitionError("Không thể chuyển sang Phân công: Đợt chưa có hồ sơ sinh viên nào!")
        hop_le = True

    elif trang_thai_cu == DotTrangThai.PHAN_CONG and trang_thai_moi == DotTrangThai.CHOT_DE_TAI:
        # Điều kiện: Bản phân công phải ở trạng thái DA_CONG_BO
        from phancong.models import ban_phan_cong
        bpc = ban_phan_cong.objects.filter(dot=dot_obj, trang_thai=BanPhanCongTrangThai.DA_CONG_BO).first()
        if not bpc:
            raise StateTransitionError("Không thể chuyển sang Chốt đề tài: Bản phân công hướng dẫn chưa được công bố chính thức!")
        hop_le = True

    elif trang_thai_cu == DotTrangThai.CHOT_DE_TAI and trang_thai_moi == DotTrangThai.THUC_HIEN:
        hop_le = True

    elif trang_thai_cu == DotTrangThai.THUC_HIEN and trang_thai_moi == DotTrangThai.CHAM_DIEM:
        hop_le = True

    elif trang_thai_cu == DotTrangThai.CHAM_DIEM and trang_thai_moi == DotTrangThai.HOAN_TAT:
        hop_le = True

    if not hop_le:
        raise StateTransitionError(f"Chuyển trạng thái không hợp lệ: Từ {trang_thai_cu} sang {trang_thai_moi}")

    # 2. Cập nhật trạng thái
    dot_obj.trang_thai = trang_thai_moi
    dot_obj.save(update_fields=["trang_thai"])

    # 3. Ghi nhật ký hệ thống
    nhat_ky_he_thong.objects.create(
        nguoi_thuc_hien=nguoi_thuc_hien,
        hanh_dong="CHUYEN_TRANG_THAI_DOT",
        doi_tuong_loai="dot",
        doi_tuong_id=dot_obj.id,
        mo_ta=f"Chuyển trạng thái đợt {dot_obj.ma_dot} từ [{trang_thai_cu}] sang [{trang_thai_moi}]. {ly_do}".strip(),
        dia_chi_ip=ip_address,
        thoi_gian=timezone.now()
    )

    return dot_obj


@transaction.atomic
def chuyen_trang_thai_ho_so(ho_so_obj, trang_thai_moi, nguoi_thuc_hien, ly_do="", ip_address=None):
    """
    Chuyển trạng thái của một hồ sơ sinh viên.
    Tự động cập nhật ngay_cap_nhat và ghi nhật ký hệ thống (không ghi điểm số).
    """
    trang_thai_cu = ho_so_obj.trang_thai
    if trang_thai_cu == trang_thai_moi:
        return ho_so_obj

    # Danh sách thứ tự trạng thái cho phép
    ds_trang_thai = [
        HoSoTrangThai.TRONG_DANH_SACH,
        HoSoTrangThai.CHO_XAC_NHAN,
        HoSoTrangThai.CHO_CHOT_DE_TAI,
        HoSoTrangThai.DANG_THUC_HIEN,
        HoSoTrangThai.CHAM_HUONG_DAN,
        HoSoTrangThai.CHO_PHAN_BIEN,
        HoSoTrangThai.HOAN_TAT,
    ]

    # Cập nhật trạng thái
    ho_so_obj.trang_thai = trang_thai_moi
    ho_so_obj.ngay_cap_nhat = timezone.now()
    ho_so_obj.save(update_fields=["trang_thai", "ngay_cap_nhat"])

    # Ghi nhật ký hệ thống
    nhat_ky_he_thong.objects.create(
        nguoi_thuc_hien=nguoi_thuc_hien,
        hanh_dong="CHUYEN_TRANG_THAI_HO_SO",
        doi_tuong_loai="ho_so",
        doi_tuong_id=ho_so_obj.id,
        mo_ta=f"Chuyển trạng thái hồ sơ SV {ho_so_obj.sinh_vien.ma_sinh_vien} từ [{trang_thai_cu}] sang [{trang_thai_moi}]. {ly_do}".strip(),
        dia_chi_ip=ip_address,
        thoi_gian=timezone.now()
    )

    return ho_so_obj
