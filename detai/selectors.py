"""
Selectors truy vấn dữ liệu cho app detai: Quản lý & Chốt đề tài (UC12, UC13, UC14, UC15).
Tuân thủ phân tầng kiến trúc Django MVT: Selectors thuần truy vấn, tối ưu hóa qua prefetch & select_related.
"""
from typing import Optional, Dict, Any, List
from django.db.models import Count, Q
from core.constants import (
    DotTrangThai,
    HoSoTrangThai,
    DeTaiGoiYTrangThai,
    DeTaiNguon,
    DeTaiTrangThai,
)
from dots.models import dot
from organization.models import giang_vien, bo_mon
from hoso.models import ho_so
from detai.models import de_tai_goi_y, de_tai


def lay_dot_chot_de_tai(dot_id: Optional[int] = None) -> Optional[dot]:
    """Lấy đợt đang ở giai đoạn CHOT_DE_TAI hoặc đợt được chỉ định"""
    if dot_id:
        return dot.objects.filter(id=dot_id).select_related("khoa").first()
    return dot.objects.filter(
        trang_thai__in=[DotTrangThai.CHOT_DE_TAI, DotTrangThai.PHAN_CONG, DotTrangThai.THUC_HIEN, DotTrangThai.CHUAN_BI]
    ).select_related("khoa").order_by("-id").first()


def lay_danh_sach_de_tai_goi_y_cua_gv(giang_vien_obj: giang_vien, dot_obj: dot) -> List[Dict[str, Any]]:
    """
    Lấy danh sách các đề tài gợi ý mà giảng viên đã đưa ra trong đợt, tính toán số SV đã chọn (UC12).
    """
    qs = de_tai_goi_y.objects.filter(
        dot=dot_obj,
        giang_vien=giang_vien_obj
    ).order_by("-id")

    res = []
    for gy in qs:
        da_chon_count = de_tai.objects.filter(
            de_tai_goi_y=gy,
            trang_thai__in=[DeTaiTrangThai.CHO_CHOT, DeTaiTrangThai.DA_CHOT]
        ).count()
        con_lai = max(0, gy.so_luong_toi_da - da_chon_count)

        res.append({
            "obj": gy,
            "id": gy.id,
            "ma_de_tai": f"DT-{gy.id:03d}",
            "ten_de_tai": gy.ten_de_tai,
            "mo_ta": gy.mo_ta,
            "so_luong_toi_da": gy.so_luong_toi_da,
            "da_chon_count": da_chon_count,
            "con_lai": con_lai,
            "trang_thai": gy.trang_thai,
            "trang_thai_text": "Đang mở" if gy.trang_thai == DeTaiGoiYTrangThai.MO else "Đã đóng",
            "con_nhan_dang_ky": (gy.trang_thai == DeTaiGoiYTrangThai.MO and con_lai > 0),
        })

    return res


def lay_de_tai_goi_y_cho_sinh_vien(ho_so_obj: ho_so) -> List[Dict[str, Any]]:
    """
    Lấy danh sách đề tài gợi ý của GVHD phụ trách hồ sơ để sinh viên chọn (UC13).
    """
    if not ho_so_obj.giang_vien_huong_dan:
        return []

    gv = ho_so_obj.giang_vien_huong_dan
    qs = de_tai_goi_y.objects.filter(
        dot=ho_so_obj.dot,
        giang_vien=gv,
        trang_thai=DeTaiGoiYTrangThai.MO
    ).order_by("-id")

    res = []
    for gy in qs:
        da_chon_count = de_tai.objects.filter(
            de_tai_goi_y=gy,
            trang_thai__in=[DeTaiTrangThai.CHO_CHOT, DeTaiTrangThai.DA_CHOT]
        ).exclude(ho_so=ho_so_obj).count()
        con_lai = max(0, gy.so_luong_toi_da - da_chon_count)

        res.append({
            "id": gy.id,
            "ma_de_tai": f"DT-{gy.id:03d}",
            "ten_de_tai": gy.ten_de_tai,
            "mo_ta": gy.mo_ta,
            "so_luong_toi_da": gy.so_luong_toi_da,
            "da_chon_count": da_chon_count,
            "con_lai": con_lai,
            "het_cho": (con_lai <= 0),
        })

    return res


def lay_hang_doi_duyet_de_tai_cho_gv(giang_vien_obj: giang_vien, dot_obj: dot) -> Dict[str, Any]:
    """
    Lấy toàn bộ hồ sơ sinh viên mà GVHD đang hướng dẫn trong đợt kèm trạng thái đề tài (UC15).
    """
    cac_ho_so = ho_so.objects.filter(
        dot=dot_obj,
        giang_vien_huong_dan=giang_vien_obj
    ).select_related(
        "sinh_vien__nguoi_dung",
        "sinh_vien__khoa",
        "de_tai_hien_tai"
    ).order_by("sinh_vien__ma_sinh_vien")

    cho_duyet_list = []
    da_chot_list = []
    chua_gui_list = []
    tra_lai_list = []

    for hs in cac_ho_so:
        dt_moi_nhat = de_tai.objects.filter(ho_so=hs).order_by("-id").first()

        item = {
            "ho_so": hs,
            "sinh_vien": hs.sinh_vien,
            "de_tai": dt_moi_nhat,
            "ten_de_tai": dt_moi_nhat.ten_de_tai if dt_moi_nhat else "Chưa đăng ký đề tài",
            "mo_ta": dt_moi_nhat.mo_ta if dt_moi_nhat else "",
            "nguon": dt_moi_nhat.nguon if dt_moi_nhat else None,
            "nguon_text": dt_moi_nhat.get_nguon_display() if dt_moi_nhat else "Chưa đăng ký",
            "trang_thai": dt_moi_nhat.trang_thai if dt_moi_nhat else "CHUA_GUI",
            "trang_thai_text": dt_moi_nhat.get_trang_thai_display() if dt_moi_nhat else "Chưa gửi đề tài",
            "gop_y": dt_moi_nhat.gop_y_cua_gv if dt_moi_nhat else "",
            "ngay_gui": dt_moi_nhat.ngay_gui.strftime("%d/%m/%Y %H:%M") if (dt_moi_nhat and dt_moi_nhat.ngay_gui) else "--",
            "ngay_chot": dt_moi_nhat.ngay_chot.strftime("%d/%m/%Y") if (dt_moi_nhat and dt_moi_nhat.ngay_chot) else "--",
        }

        if not dt_moi_nhat:
            chua_gui_list.append(item)
        elif dt_moi_nhat.trang_thai == DeTaiTrangThai.CHO_CHOT:
            cho_duyet_list.append(item)
        elif dt_moi_nhat.trang_thai == DeTaiTrangThai.DA_CHOT:
            da_chot_list.append(item)
        elif dt_moi_nhat.trang_thai == DeTaiTrangThai.TRA_LAI:
            tra_lai_list.append(item)

    return {
        "tong_so_sv": len(cac_ho_so),
        "cho_duyet_count": len(cho_duyet_list),
        "da_chot_count": len(da_chot_list),
        "chua_gui_count": len(chua_gui_list),
        "tra_lai_count": len(tra_lai_list),
        "danh_sach_cho_duyet": cho_duyet_list,
        "danh_sach_da_chot": da_chot_list,
        "danh_sach_chua_gui": chua_gui_list,
        "danh_sach_tra_lai": tra_lai_list,
    }


def lay_du_lieu_dashboard_sprint3(
    dot_obj: dot,
    bo_mon_id: Optional[int] = None,
    search_query: Optional[str] = None
) -> Dict[str, Any]:
    """
    Chuẩn bị dữ liệu hiển thị toàn khoa cho Trưởng khoa theo dõi tiến độ duyệt đề tài (Sprint 3 Dashboard).
    Khớp 100% với giao diện templates/sprint3/dashboard.html.
    """
    qs_ho_so = ho_so.objects.filter(
        dot=dot_obj
    ).select_related(
        "sinh_vien__nguoi_dung",
        "giang_vien_huong_dan__nguoi_dung",
        "giang_vien_huong_dan__bo_mon",
        "de_tai_hien_tai"
    ).order_by("sinh_vien__ma_sinh_vien")

    if bo_mon_id:
        qs_ho_so = qs_ho_so.filter(giang_vien_huong_dan__bo_mon_id=bo_mon_id)

    danh_sach_cho_duyet = []
    danh_sach_da_chot = []
    sv_de_xuat_count = 0

    for hs in qs_ho_so:
        dt = hs.de_tai_hien_tai or de_tai.objects.filter(ho_so=hs).order_by("-id").first()
        if not dt:
            continue

        gv = hs.giang_vien_huong_dan
        sv = hs.sinh_vien

        nguon_text = "Sinh viên tự đề xuất" if dt.nguon == DeTaiNguon.SV_DE_XUAT else "Ngân hàng đề tài GV"
        if dt.nguon == DeTaiNguon.SV_DE_XUAT:
            sv_de_xuat_count += 1

        item = {
            "id": dt.id,
            "ho_so_id": hs.id,
            "ma_sv": sv.ma_sinh_vien,
            "ten_sv": sv.nguoi_dung.ho_ten,
            "lop": sv.lop or "--",
            "ten_de_tai": dt.ten_de_tai,
            "gvhd": f"{gv.hoc_vi or ''} {gv.nguoi_dung.ho_ten}".strip() if gv else "Chưa gán GVHD",
            "bo_mon": gv.bo_mon.ten_bo_mon if (gv and gv.bo_mon) else "--",
            "nguon": dt.nguon,
            "nguon_text": nguon_text,
            "trang_thai": dt.trang_thai,
            "trang_thai_text": dt.get_trang_thai_display(),
            "ngay_nop": dt.ngay_gui.strftime("%d/%m/%Y %H:%M") if dt.ngay_gui else "--",
            "ngay_chot": dt.ngay_chot.strftime("%d/%m/%Y") if dt.ngay_chot else "--",
            "muc_tieu": dt.mo_ta or "Đang hoàn thiện mục tiêu nghiên cứu cụ thể.",
            "cong_nghe": "Theo hướng dẫn của Giảng viên hướng dẫn",
        }

        if dt.trang_thai == DeTaiTrangThai.CHO_CHOT:
            danh_sach_cho_duyet.append(item)
        elif dt.trang_thai == DeTaiTrangThai.DA_CHOT or hs.trang_thai == HoSoTrangThai.DANG_THUC_HIEN:
            danh_sach_da_chot.append(item)

    # Lọc tìm kiếm
    if search_query:
        q_lower = search_query.strip().lower()
        danh_sach_cho_duyet = [
            it for it in danh_sach_cho_duyet
            if q_lower in it["ma_sv"].lower()
            or q_lower in it["ten_sv"].lower()
            or q_lower in it["ten_de_tai"].lower()
            or q_lower in it["gvhd"].lower()
        ]
        danh_sach_da_chot = [
            it for it in danh_sach_da_chot
            if q_lower in it["ma_sv"].lower()
            or q_lower in it["ten_sv"].lower()
            or q_lower in it["ten_de_tai"].lower()
            or q_lower in it["gvhd"].lower()
        ]

    # Ngân hàng đề tài gợi ý toàn khoa
    qs_gy = de_tai_goi_y.objects.filter(
        dot=dot_obj
    ).select_related(
        "giang_vien__nguoi_dung",
        "giang_vien__bo_mon"
    ).order_by("-id")

    ngan_hang_goi_y = []
    goi_y_con_cho_count = 0
    for gy in qs_gy:
        da_chon = de_tai.objects.filter(
            de_tai_goi_y=gy,
            trang_thai__in=[DeTaiTrangThai.CHO_CHOT, DeTaiTrangThai.DA_CHOT]
        ).count()
        con_lai = max(0, gy.so_luong_toi_da - da_chon)
        if gy.trang_thai == DeTaiGoiYTrangThai.MO and con_lai > 0:
            goi_y_con_cho_count += 1
            tt_key = "CON_CHO"
            tt_text = f"Còn {con_lai} chỗ"
        elif gy.trang_thai == DeTaiGoiYTrangThai.MO:
            tt_key = "DA_HET_CHO"
            tt_text = "Đã nhận đủ"
        else:
            tt_key = "DONG"
            tt_text = "Đã đóng"

        ngan_hang_goi_y.append({
            "id": gy.id,
            "ma_de_tai": f"DT-{gy.id:03d}",
            "ten_de_tai": gy.ten_de_tai,
            "gv_de_xuat": f"{gy.giang_vien.hoc_vi or ''} {gy.giang_vien.nguoi_dung.ho_ten}".strip(),
            "bo_mon": gy.giang_vien.bo_mon.ten_bo_mon if gy.giang_vien.bo_mon else "--",
            "so_sv_toi_da": gy.so_luong_toi_da,
            "da_dang_ky": da_chon,
            "con_lai": con_lai,
            "trang_thai": tt_key,
            "trang_thai_text": tt_text,
            "mo_ta": gy.mo_ta or "Chưa có mô tả chi tiết.",
        })

    tong_sinh_vien = qs_ho_so.count()
    da_chot_total = len(danh_sach_da_chot)
    cho_duyet_total = len(danh_sach_cho_duyet)
    phan_tram_chot = round((da_chot_total / tong_sinh_vien) * 100) if tong_sinh_vien > 0 else 0

    return {
        "current_dot": dot_obj,
        "danh_sach_cho_duyet": danh_sach_cho_duyet,
        "danh_sach_da_chot": danh_sach_da_chot,
        "ngan_hang_goi_y": ngan_hang_goi_y,
        "danh_sach_bo_mon": list(bo_mon.objects.filter(khoa=dot_obj.khoa)),
        "kpi": {
            "quota_tong": tong_sinh_vien,
            "quota_phan_bo": tong_sinh_vien,
            "da_chot": da_chot_total,
            "cho_duyet": cho_duyet_total,
            "goi_y_tong": len(ngan_hang_goi_y),
            "goi_y_con_cho": goi_y_con_cho_count,
            "phan_tram_chot": phan_tram_chot,
            "sv_de_xuat_count": sv_de_xuat_count,
        }
    }
