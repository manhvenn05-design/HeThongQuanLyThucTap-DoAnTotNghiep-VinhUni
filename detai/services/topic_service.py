"""
Tầng Services nghiệp vụ cho app detai: Đăng ký & Chốt đề tài (UC12, UC13, UC14, UC15).
Tuân thủ nghiêm ngặt quy tắc GEMINI.md:
- Logic chuyển trạng thái hồ sơ bắt buộc gọi qua core.state.chuyen_trang_thai_ho_so.
- Validate chặt chẽ các ràng buộc nghiệp vụ (hạn mức, nguồn đề tài, lý do từ chối/trả lại).
"""
from typing import Optional, List, Dict, Any
from django.db import transaction
from django.utils import timezone
from core.constants import (
    DotTrangThai,
    HoSoTrangThai,
    DeTaiGoiYTrangThai,
    DeTaiNguon,
    DeTaiTrangThai,
)
from dots.models import dot
from organization.models import giang_vien
from hoso.models import ho_so
from detai.models import de_tai_goi_y, de_tai
from hethong.models import thong_bao, nhat_ky_he_thong
from core.state import chuyen_trang_thai_ho_so


class TopicValidationError(Exception):
    """Lỗi vi phạm ràng buộc nghiệp vụ đề tài"""
    pass


# ==============================================================================
# UC12: ĐƯA RA ĐỀ TÀI GỢI Ý CỦA GIẢNG VIÊN HƯỚNG DẪN
# ==============================================================================

@transaction.atomic
def tao_de_tai_goi_y(
    dot_obj: dot,
    giang_vien_obj: giang_vien,
    ten_de_tai: str,
    mo_ta: str = "",
    so_luong_toi_da: int = 1,
    nguoi_thuc_hien = None,
    ip_address: Optional[str] = None
) -> de_tai_goi_y:
    """
    Giảng viên hướng dẫn tạo đề tài gợi ý cho đợt (UC12).
    """
    ten_de_tai = ten_de_tai.strip()
    if not ten_de_tai:
        raise TopicValidationError("Tên đề tài gợi ý không được để trống!")

    if so_luong_toi_da < 1:
        raise TopicValidationError("Số lượng sinh viên tối đa có thể chọn phải ít nhất là 1!")

    obj = de_tai_goi_y.objects.create(
        dot=dot_obj,
        giang_vien=giang_vien_obj,
        ten_de_tai=ten_de_tai,
        mo_ta=mo_ta.strip() if mo_ta else "",
        so_luong_toi_da=so_luong_toi_da,
        trang_thai=DeTaiGoiYTrangThai.MO
    )

    if nguoi_thuc_hien:
        nhat_ky_he_thong.objects.create(
            nguoi_thuc_hien=nguoi_thuc_hien,
            hanh_dong="TAO_DE_TAI_GOI_Y",
            doi_tuong_loai="de_tai_goi_y",
            doi_tuong_id=obj.id,
            mo_ta=f"GV {giang_vien_obj.nguoi_dung.ho_ten} tạo đề tài gợi ý: '{ten_de_tai}'",
            dia_chi_ip=ip_address,
            thoi_gian=timezone.now()
        )

    return obj


@transaction.atomic
def dong_hoac_mo_de_tai_goi_y(
    de_tai_goi_y_obj: de_tai_goi_y,
    mo_dang_ky: bool,
    nguoi_thuc_hien = None,
    ip_address: Optional[str] = None
) -> de_tai_goi_y:
    """Bật/tắt trạng thái nhận đăng ký của một đề tài gợi ý."""
    trang_thai_moi = DeTaiGoiYTrangThai.MO if mo_dang_ky else DeTaiGoiYTrangThai.DONG
    if de_tai_goi_y_obj.trang_thai != trang_thai_moi:
        de_tai_goi_y_obj.trang_thai = trang_thai_moi
        de_tai_goi_y_obj.save(update_fields=["trang_thai"])

        if nguoi_thuc_hien:
            nhat_ky_he_thong.objects.create(
                nguoi_thuc_hien=nguoi_thuc_hien,
                hanh_dong="DOI_TRANG_THAI_DE_TAI_GOI_Y",
                doi_tuong_loai="de_tai_goi_y",
                doi_tuong_id=de_tai_goi_y_obj.id,
                mo_ta=f"Đổi trạng thái đề tài gợi ý '{de_tai_goi_y_obj.ten_de_tai}' thành [{trang_thai_moi}]",
                dia_chi_ip=ip_address,
                thoi_gian=timezone.now()
            )

    return de_tai_goi_y_obj


# ==============================================================================
# UC13: SINH VIÊN CHỌN ĐỀ TÀI TỪ GỢI Ý CỦA GVHD
# ==============================================================================

@transaction.atomic
def sinh_vien_chon_de_tai_goi_y(
    ho_so_obj: ho_so,
    de_tai_goi_y_obj: de_tai_goi_y,
    nguoi_thuc_hien = None,
    ip_address: Optional[str] = None
) -> de_tai:
    """
    Sinh viên đăng ký một đề tài trong danh sách gợi ý của chính GVHD phụ trách (UC13).
    """
    # 1. Kiểm tra trạng thái hồ sơ
    if ho_so_obj.trang_thai != HoSoTrangThai.CHO_CHOT_DE_TAI:
        raise TopicValidationError(
            f"Hồ sơ đang ở trạng thái [{ho_so_obj.get_trang_thai_display()}], không thể đăng ký đề tài!"
        )

    # 2. Kiểm tra GVHD phụ trách
    if not ho_so_obj.giang_vien_huong_dan:
        raise TopicValidationError("Hồ sơ chưa được phân công Giảng viên hướng dẫn chính thức!")

    if de_tai_goi_y_obj.giang_vien != ho_so_obj.giang_vien_huong_dan:
        raise TopicValidationError("Bạn chỉ được chọn đề tài gợi ý do chính Giảng viên hướng dẫn của mình đưa ra!")

    # 3. Kiểm tra trạng thái mở của đề tài gợi ý
    if de_tai_goi_y_obj.trang_thai != DeTaiGoiYTrangThai.MO:
        raise TopicValidationError("Đề tài gợi ý này hiện đang đóng, không nhận thêm đăng ký!")

    # 4. Kiểm tra số lượng đã đăng ký còn chỗ
    da_dang_ky_count = de_tai.objects.filter(
        de_tai_goi_y=de_tai_goi_y_obj,
        trang_thai__in=[DeTaiTrangThai.CHO_CHOT, DeTaiTrangThai.DA_CHOT]
    ).exclude(ho_so=ho_so_obj).count()

    if da_dang_ky_count >= de_tai_goi_y_obj.so_luong_toi_da:
        raise TopicValidationError("Đề tài gợi ý này đã đủ số lượng sinh viên đăng ký!")

    # 5. Kiểm tra hồ sơ đã có đề tài chờ chốt hoặc đã chốt chưa
    de_tai_hien_co = de_tai.objects.filter(
        ho_so=ho_so_obj,
        trang_thai__in=[DeTaiTrangThai.CHO_CHOT, DeTaiTrangThai.DA_CHOT]
    ).first()
    if de_tai_hien_co:
        if de_tai_hien_co.trang_thai == DeTaiTrangThai.DA_CHOT:
            raise TopicValidationError("Hồ sơ của bạn đã được chốt đề tài chính thức, không thể chọn đề tài khác!")
        # Nếu đang có đề tài CHO_CHOT, cập nhật sang đề tài mới
        de_tai_hien_co.nguon = DeTaiNguon.GV_DUA_RA
        de_tai_hien_co.de_tai_goi_y = de_tai_goi_y_obj
        de_tai_hien_co.ten_de_tai = de_tai_goi_y_obj.ten_de_tai
        de_tai_hien_co.mo_ta = de_tai_goi_y_obj.mo_ta
        de_tai_hien_co.trang_thai = DeTaiTrangThai.CHO_CHOT
        de_tai_hien_co.gop_y_cua_gv = ""
        de_tai_hien_co.ngay_gui = timezone.now()
        de_tai_hien_co.save()
        dt_obj = de_tai_hien_co
    else:
        dt_obj = de_tai.objects.create(
            ho_so=ho_so_obj,
            nguon=DeTaiNguon.GV_DUA_RA,
            de_tai_goi_y=de_tai_goi_y_obj,
            ten_de_tai=de_tai_goi_y_obj.ten_de_tai,
            mo_ta=de_tai_goi_y_obj.mo_ta,
            trang_thai=DeTaiTrangThai.CHO_CHOT,
            ngay_gui=timezone.now()
        )

    # 6. Gửi thông báo đến GVHD
    if ho_so_obj.giang_vien_huong_dan and ho_so_obj.giang_vien_huong_dan.nguoi_dung:
        thong_bao.objects.create(
            nguoi_nhan=ho_so_obj.giang_vien_huong_dan.nguoi_dung,
            loai="DANG_KY_DE_TAI",
            tieu_de=f"Sinh viên {ho_so_obj.sinh_vien.nguoi_dung.ho_ten} đã chọn đề tài gợi ý",
            noi_dung=f"Sinh viên {ho_so_obj.sinh_vien.nguoi_dung.ho_ten} ({ho_so_obj.sinh_vien.ma_sinh_vien}) đã chọn đề tài: '{dt_obj.ten_de_tai}'"
        )

    if nguoi_thuc_hien:
        nhat_ky_he_thong.objects.create(
            nguoi_thuc_hien=nguoi_thuc_hien,
            hanh_dong="CHON_DE_TAI_GOI_Y",
            doi_tuong_loai="de_tai",
            doi_tuong_id=dt_obj.id,
            mo_ta=f"SV {ho_so_obj.sinh_vien.ma_sinh_vien} chọn đề tài gợi ý: '{dt_obj.ten_de_tai}'",
            dia_chi_ip=ip_address,
            thoi_gian=timezone.now()
        )

    return dt_obj


# ==============================================================================
# UC14: SINH VIÊN TỰ ĐỀ XUẤT ĐỀ TÀI MỚI
# ==============================================================================

@transaction.atomic
def sinh_vien_de_xuat_de_tai(
    ho_so_obj: ho_so,
    ten_de_tai: str,
    mo_ta: str = "",
    nguoi_thuc_hien = None,
    ip_address: Optional[str] = None
) -> de_tai:
    """
    Sinh viên tự đề xuất tên đề tài và mô tả nội dung cho GVHD duyệt (UC14).
    """
    ten_de_tai = ten_de_tai.strip()
    if not ten_de_tai:
        raise TopicValidationError("Tên đề tài đề xuất không được để trống!")

    if ho_so_obj.trang_thai != HoSoTrangThai.CHO_CHOT_DE_TAI:
        raise TopicValidationError(
            f"Hồ sơ đang ở trạng thái [{ho_so_obj.get_trang_thai_display()}], không thể nộp đề xuất đề tài!"
        )

    if not ho_so_obj.giang_vien_huong_dan:
        raise TopicValidationError("Hồ sơ chưa có Giảng viên hướng dẫn chính thức!")

    de_tai_hien_co = de_tai.objects.filter(
        ho_so=ho_so_obj,
        trang_thai__in=[DeTaiTrangThai.CHO_CHOT, DeTaiTrangThai.DA_CHOT]
    ).first()

    if de_tai_hien_co:
        if de_tai_hien_co.trang_thai == DeTaiTrangThai.DA_CHOT:
            raise TopicValidationError("Đề tài của bạn đã được duyệt chốt chính thức, không thể thay đổi!")
        de_tai_hien_co.nguon = DeTaiNguon.SV_DE_XUAT
        de_tai_hien_co.de_tai_goi_y = None
        de_tai_hien_co.ten_de_tai = ten_de_tai
        de_tai_hien_co.mo_ta = mo_ta.strip() if mo_ta else ""
        de_tai_hien_co.trang_thai = DeTaiTrangThai.CHO_CHOT
        de_tai_hien_co.gop_y_cua_gv = ""
        de_tai_hien_co.ngay_gui = timezone.now()
        de_tai_hien_co.save()
        dt_obj = de_tai_hien_co
    else:
        dt_obj = de_tai.objects.create(
            ho_so=ho_so_obj,
            nguon=DeTaiNguon.SV_DE_XUAT,
            de_tai_goi_y=None,
            ten_de_tai=ten_de_tai,
            mo_ta=mo_ta.strip() if mo_ta else "",
            trang_thai=DeTaiTrangThai.CHO_CHOT,
            ngay_gui=timezone.now()
        )

    if ho_so_obj.giang_vien_huong_dan and ho_so_obj.giang_vien_huong_dan.nguoi_dung:
        thong_bao.objects.create(
            nguoi_nhan=ho_so_obj.giang_vien_huong_dan.nguoi_dung,
            loai="DE_XUAT_DE_TAI",
            tieu_de=f"Sinh viên {ho_so_obj.sinh_vien.nguoi_dung.ho_ten} gửi đề xuất đề tài mới",
            noi_dung=f"Sinh viên {ho_so_obj.sinh_vien.nguoi_dung.ho_ten} ({ho_so_obj.sinh_vien.ma_sinh_vien}) đề xuất đề tài: '{dt_obj.ten_de_tai}'"
        )

    if nguoi_thuc_hien:
        nhat_ky_he_thong.objects.create(
            nguoi_thuc_hien=nguoi_thuc_hien,
            hanh_dong="DE_XUAT_DE_TAI",
            doi_tuong_loai="de_tai",
            doi_tuong_id=dt_obj.id,
            mo_ta=f"SV {ho_so_obj.sinh_vien.ma_sinh_vien} đề xuất đề tài: '{dt_obj.ten_de_tai}'",
            dia_chi_ip=ip_address,
            thoi_gian=timezone.now()
        )

    return dt_obj


# ==============================================================================
# UC15: GVHD DUYỆT CHỐT HOẶC TRẢ LẠI ĐỀ TÀI
# ==============================================================================

@transaction.atomic
def gvhd_phe_duyet_de_tai(
    de_tai_obj: de_tai,
    chap_nhan: bool,
    gop_y: str = "",
    nguoi_thuc_hien = None,
    ip_address: Optional[str] = None
) -> de_tai:
    """
    GVHD duyệt chốt (chấp nhận) hoặc trả lại đề tài (UC15).
    - Chấp nhận: de_tai DA_CHOT, gán ho_so.de_tai_hien_tai, ho_so chuyển DANG_THUC_HIEN.
    - Trả lại: de_tai TRA_LAI + bắt buộc nhập góp ý; ho_so giữ nguyên CHO_CHOT_DE_TAI.
    """
    if de_tai_obj.trang_thai != DeTaiTrangThai.CHO_CHOT:
        raise TopicValidationError(
            f"Đề tài đang ở trạng thái [{de_tai_obj.get_trang_thai_display()}], không thể xử lý lại!"
        )

    hs = de_tai_obj.ho_so
    sv = hs.sinh_vien

    if chap_nhan:
        de_tai_obj.trang_thai = DeTaiTrangThai.DA_CHOT
        de_tai_obj.ngay_chot = timezone.now()
        de_tai_obj.save(update_fields=["trang_thai", "ngay_chot"])

        # Gán đề tài chính thức cho hồ sơ
        hs.de_tai_hien_tai = de_tai_obj
        hs.save(update_fields=["de_tai_hien_tai"])

        # Chuyển trạng thái hồ sơ sang DANG_THUC_HIEN qua Dịch vụ tập trung (core/state.py)
        chuyen_trang_thai_ho_so(
            ho_so_obj=hs,
            trang_thai_moi=HoSoTrangThai.DANG_THUC_HIEN,
            nguoi_thuc_hien=nguoi_thuc_hien or hs.giang_vien_huong_dan.nguoi_dung,
            ly_do=f"GVHD đã duyệt chốt đề tài: '{de_tai_obj.ten_de_tai}'",
            ip_address=ip_address
        )

        # Nếu đề tài chọn từ gợi ý, kiểm tra xem đã đủ số lượng tối đa để đóng đăng ký không
        if de_tai_obj.de_tai_goi_y:
            gy = de_tai_obj.de_tai_goi_y
            da_chot_count = de_tai.objects.filter(
                de_tai_goi_y=gy,
                trang_thai=DeTaiTrangThai.DA_CHOT
            ).count()
            if da_chot_count >= gy.so_luong_toi_da and gy.trang_thai == DeTaiGoiYTrangThai.MO:
                gy.trang_thai = DeTaiGoiYTrangThai.DONG
                gy.save(update_fields=["trang_thai"])

        # Thông báo cho sinh viên
        thong_bao.objects.create(
            nguoi_nhan=sv.nguoi_dung,
            loai="DE_TAI_DA_CHOT",
            tieu_de="Đề tài của bạn đã được GVHD duyệt chốt chính thức",
            noi_dung=f"Thầy/Cô hướng dẫn đã phê duyệt chính thức đề tài: '{de_tai_obj.ten_de_tai}'. Bạn có thể bắt đầu triển khai đồ án và nộp minh chứng tuần."
        )

    else:
        gop_y = gop_y.strip()
        if not gop_y:
            raise TopicValidationError("Bắt buộc phải nhập ý kiến góp ý / yêu cầu chỉnh sửa khi trả lại đề tài!")

        de_tai_obj.trang_thai = DeTaiTrangThai.TRA_LAI
        de_tai_obj.gop_y_cua_gv = gop_y
        de_tai_obj.save(update_fields=["trang_thai", "gop_y_cua_gv"])

        # Hồ sơ giữ nguyên CHO_CHOT_DE_TAI
        # Thông báo cho sinh viên
        thong_bao.objects.create(
            nguoi_nhan=sv.nguoi_dung,
            loai="DE_TAI_TRA_LAI",
            tieu_de="GVHD yêu cầu chỉnh sửa đề tài đồ án",
            noi_dung=f"GVHD đã trả lại đề tài '{de_tai_obj.ten_de_tai}' kèm góp ý: {gop_y}. Vui lòng hoàn thiện và gửi lại."
        )

        if nguoi_thuc_hien:
            nhat_ky_he_thong.objects.create(
                nguoi_thuc_hien=nguoi_thuc_hien,
                hanh_dong="TRA_LAI_DE_TAI",
                doi_tuong_loai="de_tai",
                doi_tuong_id=de_tai_obj.id,
                mo_ta=f"GVHD trả lại đề tài của SV {sv.ma_sinh_vien}. Góp ý: {gop_y}",
                dia_chi_ip=ip_address,
                thoi_gian=timezone.now()
            )

    return de_tai_obj


@transaction.atomic
def gvhd_duyet_hang_loat_de_tai(
    danh_sach_de_tai_ids: List[int],
    giang_vien_obj: giang_vien,
    nguoi_thuc_hien = None,
    ip_address: Optional[str] = None
) -> int:
    """
    GVHD duyệt đồng loạt danh sách các đề tài hợp lệ đang chờ duyệt (UC15).
    """
    qs = de_tai.objects.filter(
        id__in=danh_sach_de_tai_ids,
        ho_so__giang_vien_huong_dan=giang_vien_obj,
        trang_thai=DeTaiTrangThai.CHO_CHOT
    ).select_related("ho_so__sinh_vien__nguoi_dung", "de_tai_goi_y")

    count = 0
    for dt in qs:
        gvhd_phe_duyet_de_tai(
            de_tai_obj=dt,
            chap_nhan=True,
            gop_y="",
            nguoi_thuc_hien=nguoi_thuc_hien or giang_vien_obj.nguoi_dung,
            ip_address=ip_address
        )
        count += 1

    return count
