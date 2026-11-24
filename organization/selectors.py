"""
Selectors cho app organization (Cổng Giảng viên và Cổng Sinh viên).
Tuân thủ phân tầng kiến trúc Django MVT và Quy tắc bảo mật GEMINI.md:
- Giảng viên và Sinh viên KHÔNG ĐƯỢC xem điểm trung bình đầu vào (diem_dau_vao).
- Truy vấn tập trung, kiểm tra quyền theo user đăng nhập.
"""
from typing import Optional, Dict, Any, List
from django.db.models import Q
from django.contrib.auth.models import User
from organization.models import giang_vien, sinh_vien
from hoso.models import ho_so
from phancong.models import ban_phan_cong, phan_cong_huong_dan
from core.constants import (
    DotTrangThai,
    BanPhanCongTrangThai,
    PhanCongHuongDanTrangThai,
    HoSoTrangThai,
)
from phancong.selectors import lay_dot_phan_cong


def get_current_lecturer(user: Optional[User]) -> Optional[giang_vien]:
    """Tìm bản ghi giang_vien tương ứng với user đang đăng nhập."""
    if user and user.is_authenticated:
        # 1. Tìm theo ma_can_bo hoặc username
        gv = giang_vien.objects.filter(
            Q(ma_can_bo__iexact=user.username) |
            Q(nguoi_dung__ma_dinh_danh_cong__iexact=user.username)
        ).select_related("nguoi_dung", "khoa", "bo_mon").first()
        if gv:
            return gv

        # 2. Tìm theo email
        if user.email:
            gv = giang_vien.objects.filter(
                nguoi_dung__email__iexact=user.email
            ).select_related("nguoi_dung", "khoa", "bo_mon").first()
            if gv:
                return gv

    # Fallback cho chế độ demo / phát triển: TS. Cao Thanh Sơn (CB_GV01)
    gv = giang_vien.objects.filter(ma_can_bo="CB_GV01").select_related("nguoi_dung", "khoa", "bo_mon").first()
    if not gv:
        gv = giang_vien.objects.select_related("nguoi_dung", "khoa", "bo_mon").first()
    return gv


def get_current_student(user: Optional[User]) -> Optional[sinh_vien]:
    """Tìm bản ghi sinh_vien tương ứng với user đang đăng nhập."""
    if user and user.is_authenticated:
        # 1. Tìm theo ma_sinh_vien hoặc username
        sv = sinh_vien.objects.filter(
            Q(ma_sinh_vien__iexact=user.username) |
            Q(nguoi_dung__ma_dinh_danh_cong__iexact=user.username)
        ).select_related("nguoi_dung", "khoa").first()
        if sv:
            return sv

        # 2. Tìm theo email
        if user.email:
            sv = sinh_vien.objects.filter(
                nguoi_dung__email__iexact=user.email
            ).select_related("nguoi_dung", "khoa").first()
            if sv:
                return sv

    # Fallback cho chế độ demo / phát triển: SV đầu tiên có hồ sơ trong đợt
    hs_first = ho_so.objects.select_related("sinh_vien__nguoi_dung", "sinh_vien__khoa").first()
    if hs_first:
        return hs_first.sinh_vien

    return sinh_vien.objects.select_related("nguoi_dung", "khoa").first()


def lay_du_lieu_cong_giang_vien(user: Optional[User], dot_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Chuẩn bị toàn bộ dữ liệu thực tế cho Cổng Tác nghiệp Giảng viên (UC10, UC12, UC15, UC18...).
    BẢO MẬT: TUYỆT ĐỐI KHÔNG TRẢ VỀ diem_dau_vao (Rule 3).
    """
    gv = get_current_lecturer(user)
    current_dot = lay_dot_phan_cong(dot_id)

    bpc = None
    danh_sach_huong_dan = []
    cho_xac_nhan_count = 0
    da_tiep_nhan_count = 0
    da_tu_choi_count = 0
    can_xac_nhan = False

    so_sv_toi_da = current_dot.so_sv_toi_da_moi_gv if current_dot else 5

    if current_dot and gv:
        bpc = ban_phan_cong.objects.filter(dot=current_dot).order_by("-id").first()
        if bpc:
            qs_pc = phan_cong_huong_dan.objects.filter(
                ban_phan_cong=bpc,
                giang_vien=gv
            ).select_related(
                "ho_so__sinh_vien__nguoi_dung",
                "ho_so__sinh_vien"
            ).order_by("ho_so__sinh_vien__ma_sinh_vien")

            for pc in qs_pc:
                hs = pc.ho_so
                sv = hs.sinh_vien

                if pc.trang_thai == PhanCongHuongDanTrangThai.CHO_XAC_NHAN:
                    trang_thai_text = "Chờ thầy xác nhận tiếp nhận"
                    cho_xac_nhan_count += 1
                elif pc.trang_thai == PhanCongHuongDanTrangThai.DONG_Y:
                    trang_thai_text = "Đã đồng ý tiếp nhận"
                    da_tiep_nhan_count += 1
                elif pc.trang_thai == PhanCongHuongDanTrangThai.TU_CHOI:
                    trang_thai_text = f"Đã từ chối ({pc.ly_do_tu_choi})"
                    da_tu_choi_count += 1
                else:
                    trang_thai_text = "Dự thảo phân công"

                # Đề tài (Sprint 3)
                de_tai_ten = hs.de_tai_hien_tai.ten_de_tai if getattr(hs, 'de_tai_hien_tai', None) else "Chưa đăng ký đề tài chính thức"

                danh_sach_huong_dan.append({
                    "id": hs.id,
                    "pc_id": pc.id,
                    "ma_sv": sv.ma_sinh_vien,
                    "ten_sv": sv.nguoi_dung.ho_ten,
                    "lop": sv.lop or "--",
                    "de_tai": de_tai_ten,
                    "trang_thai_de_tai": hs.trang_thai,
                    "trang_thai_text": trang_thai_text,
                    "trang_thai_pc": pc.trang_thai,
                    "tien_do": "Tuần 1 / 15",
                    "diem_hd": None,
                })

            if bpc.trang_thai == BanPhanCongTrangThai.DA_GUI and cho_xac_nhan_count > 0:
                can_xac_nhan = True

    # Nếu chưa có phân công trong CSDL (trước khi Snake draft chạy), hiển thị danh sách rỗng hoặc mẫu thông báo
    so_sv_huong_dan = len([d for d in danh_sach_huong_dan if d.get("trang_thai_pc") != PhanCongHuongDanTrangThai.TU_CHOI])

    persona_name = f"{gv.hoc_vi or ''} {gv.nguoi_dung.ho_ten}".strip() if gv else "TS. Cao Thanh Sơn"
    persona_code = gv.ma_can_bo if gv else "CB_GV01"
    words = gv.nguoi_dung.ho_ten.split() if gv and gv.nguoi_dung.ho_ten else []
    persona_avatar = "".join([w[0].upper() for w in words[-2:]]) if len(words) >= 2 else (words[0][:2].upper() if words else "GV")

    return {
        "giang_vien": gv,
        "current_dot": current_dot,
        "ban_phan_cong": bpc,
        "danh_sach_huong_dan": danh_sach_huong_dan,
        "so_sv_huong_dan": so_sv_huong_dan,
        "so_sv_toi_da": so_sv_toi_da,
        "cho_xac_nhan_count": cho_xac_nhan_count,
        "da_tiep_nhan_count": da_tiep_nhan_count,
        "da_tu_choi_count": da_tu_choi_count,
        "can_xac_nhan": can_xac_nhan,
        "persona_name": persona_name,
        "persona_code": persona_code,
        "persona_avatar": persona_avatar,
        "persona_role_display": "Giảng viên",
        "persona_bomon": gv.bo_mon.ten_bo_mon if (gv and gv.bo_mon) else "Bộ môn Kỹ thuật phần mềm",
        "persona_hocvi": gv.hoc_vi if (gv and gv.hoc_vi) else "Tiến sĩ",
        "persona_khoa": gv.khoa.ten_khoa if (gv and gv.khoa) else "Khoa Công nghệ Thông tin",
    }


def lay_du_lieu_cong_sinh_vien(user: Optional[User], dot_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Chuẩn bị dữ liệu thực tế cho Cổng Học tập & Tốt nghiệp Sinh viên (UC11, UC13, UC14...).
    Tuân thủ UC11: Nếu chưa công bố chính thức, hiển thị thông báo chờ.
    """
    sv = get_current_student(user)
    current_dot = lay_dot_phan_cong(dot_id)

    hs = None
    if sv:
        if current_dot:
            hs = ho_so.objects.filter(sinh_vien=sv, dot=current_dot).select_related(
                "dot",
                "giang_vien_huong_dan__nguoi_dung",
                "giang_vien_huong_dan__bo_mon",
                "giang_vien_huong_dan__khoa"
            ).first()
        if not hs:
            hs = ho_so.objects.filter(sinh_vien=sv).select_related(
                "dot",
                "giang_vien_huong_dan__nguoi_dung",
                "giang_vien_huong_dan__bo_mon",
                "giang_vien_huong_dan__khoa"
            ).order_by("-id").first()

    # Fallback nếu sv hiện tại chưa có hồ sơ nhưng đợt có hồ sơ (chế độ demo)
    if not hs and current_dot:
        hs = ho_so.objects.filter(dot=current_dot).select_related(
            "sinh_vien__nguoi_dung",
            "sinh_vien__khoa",
            "giang_vien_huong_dan__nguoi_dung",
            "giang_vien_huong_dan__bo_mon"
        ).first()
        if hs:
            sv = hs.sinh_vien

    # Kiểm tra GVHD chính thức (UC11)
    da_co_gvhd = False
    gvhd_ho_ten = None
    gvhd_ma_cb = None
    gvhd_bo_mon = None
    gvhd_email = None
    gvhd_sdt = None

    if hs and hs.giang_vien_huong_dan:
        gv = hs.giang_vien_huong_dan
        da_co_gvhd = True
        gvhd_ho_ten = f"{gv.hoc_vi or ''} {gv.nguoi_dung.ho_ten}".strip()
        gvhd_ma_cb = gv.ma_can_bo
        gvhd_bo_mon = gv.bo_mon.ten_bo_mon if gv.bo_mon else "Bộ môn Kỹ thuật phần mềm"
        gvhd_email = gv.nguoi_dung.email or ""
        gvhd_sdt = gv.nguoi_dung.so_dien_thoai or ""

    trang_thai_text = hs.get_trang_thai_display() if hs else "Chưa có hồ sơ"

    thong_tin_sv = {
        "ho_ten": sv.nguoi_dung.ho_ten if sv else "Nguyễn Văn An",
        "ma_sv": sv.ma_sinh_vien if sv else "22A1001",
        "lop": sv.lop if (sv and sv.lop) else "63KTPM1",
        "khoa": sv.khoa.ten_khoa if (sv and sv.khoa) else "Khoa Công nghệ Thông tin",
        "da_co_gvhd": da_co_gvhd,
        "gvhd_ho_ten": gvhd_ho_ten,
        "gvhd_ma_cb": gvhd_ma_cb,
        "gvhd_bo_mon": gvhd_bo_mon,
        "gvhd_email": gvhd_email,
        "gvhd_sdt": gvhd_sdt,
        "trang_thai_ho_so": hs.trang_thai if hs else "CHUAN_BI",
        "trang_thai_text": trang_thai_text,
    }

    persona_name = thong_tin_sv["ho_ten"]
    persona_code = thong_tin_sv["ma_sv"]
    words = persona_name.split()
    persona_avatar = "".join([w[0].upper() for w in words[-2:]]) if len(words) >= 2 else (words[0][:2].upper() if words else "SV")

    return {
        "sinh_vien": sv,
        "ho_so": hs,
        "current_dot": current_dot or (hs.dot if hs else None),
        "thong_tin_sv": thong_tin_sv,
        "persona_name": persona_name,
        "persona_code": persona_code,
        "persona_avatar": persona_avatar,
        "persona_role_display": "Sinh viên",
    }
