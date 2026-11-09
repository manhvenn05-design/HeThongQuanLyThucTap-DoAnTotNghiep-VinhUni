"""
Các hàm truy vấn dữ liệu (Selectors) cho Sprint 2: Phân công Hướng dẫn (UC07, UC08, UC09, UC10, UC11).
Tuân thủ nghiêm ngặt phân tầng Django MVT và bảo mật GPA đầu vào (chỉ Trưởng khoa được xem).
"""
import math
from typing import Optional, Dict, Any, List
from django.db.models import Count, Q, Avg
from dots.models import dot
from organization.models import giang_vien, bo_mon
from hoso.models import ho_so, diem_dau_vao
from phancong.models import ban_phan_cong, phan_cong_huong_dan
from core.constants import (
    DotTrangThai,
    HoSoTrangThai,
    BanPhanCongTrangThai,
    PhanCongHuongDanTrangThai,
)


def lay_dot_phan_cong(dot_id: Optional[int] = None) -> Optional[dot]:
    """Lấy đợt đang ở giai đoạn PHAN_CONG hoặc đợt được chỉ định"""
    if dot_id:
        return dot.objects.filter(id=dot_id).select_related("khoa").first()
    # Ưu tiên đợt đang ở trạng thái PHAN_CONG hoặc CHUAN_BI
    return dot.objects.filter(
        trang_thai__in=[DotTrangThai.PHAN_CONG, DotTrangThai.CHUAN_BI, DotTrangThai.CHOT_DE_TAI]
    ).select_related("khoa").order_by("-id").first()


def lay_hoac_khoi_tao_ban_phan_cong(dot_obj: dot, nguoi_dung) -> ban_phan_cong:
    """Lấy bản phân công hiện hành hoặc tạo mới bản nháp nếu chưa có"""
    bpc = ban_phan_cong.objects.filter(dot=dot_obj).order_by("-id").first()
    if not bpc:
        bpc = ban_phan_cong.objects.create(
            dot=dot_obj,
            nguoi_tao=nguoi_dung,
            trang_thai=BanPhanCongTrangThai.NHAP
        )
    return bpc


def lay_du_lieu_dashboard_sprint2(
    dot_obj: dot,
    ban_phan_cong_obj: ban_phan_cong,
    bo_mon_filter: Optional[int] = None,
    gpa_filter: Optional[str] = None,
    search_query: Optional[str] = None
) -> Dict[str, Any]:
    """
    Chuẩn bị dữ liệu hiển thị toàn diện cho Dashboard Sprint 2 (Khung Trái + Khung Phải + KPIs).
    Được tối ưu bằng prefetch & select_related để chỉ mất 3-4 query SQL.
    """
    max_sv_per_gv = dot_obj.so_sv_toi_da_moi_gv

    # 1. Lấy toàn bộ các dòng phân công hiện tại của bản phân công
    cac_dong_phan_cong = phan_cong_huong_dan.objects.filter(
        ban_phan_cong=ban_phan_cong_obj
    ).select_related(
        "ho_so__sinh_vien__nguoi_dung",
        "ho_so__diem_dau_vao",
        "giang_vien__nguoi_dung",
        "giang_vien__bo_mon"
    )

    # Tập hợp các ho_so_id đã được gán (và không bị từ chối)
    ho_so_da_gan_map = {}
    for dong in cac_dong_phan_cong:
        if dong.trang_thai != PhanCongHuongDanTrangThai.TU_CHOI:
            ho_so_da_gan_map[dong.ho_so_id] = dong

    # 2. Danh sách hồ sơ sinh viên trong đợt
    qs_ho_so = ho_so.objects.filter(
        dot=dot_obj
    ).select_related(
        "sinh_vien__nguoi_dung",
        "diem_dau_vao"
    ).order_by("sinh_vien__ma_sinh_vien")

    danh_sach_sinh_vien_tong = list(qs_ho_so)
    tong_so_sinh_vien = len(danh_sach_sinh_vien_tong)

    # 3. Phân tách danh sách chưa gán vs đã gán
    sinh_vien_chua_gan = []
    for hs in danh_sach_sinh_vien_tong:
        if hs.id not in ho_so_da_gan_map:
            sinh_vien_chua_gan.append(hs)

    # Lọc tìm kiếm / GPA cho danh sách chưa gán
    if search_query:
        q_lower = search_query.strip().lower()
        sinh_vien_chua_gan = [
            hs for hs in sinh_vien_chua_gan
            if q_lower in hs.sinh_vien.ma_sinh_vien.lower()
            or q_lower in hs.sinh_vien.nguoi_dung.ho_ten.lower()
            or (hs.sinh_vien.lop and q_lower in hs.sinh_vien.lop.lower())
        ]

    if gpa_filter == "GIOI":  # >= 3.6
        sinh_vien_chua_gan = [
            hs for hs in sinh_vien_chua_gan
            if getattr(hs, "diem_dau_vao", None) and getattr(hs.diem_dau_vao, "diem_tb_he4", 0) and float(hs.diem_dau_vao.diem_tb_he4) >= 3.6
        ]
    elif gpa_filter == "KHA":  # 3.2 - 3.59
        sinh_vien_chua_gan = [
            hs for hs in sinh_vien_chua_gan
            if getattr(hs, "diem_dau_vao", None) and getattr(hs.diem_dau_vao, "diem_tb_he4", 0) and 3.2 <= float(hs.diem_dau_vao.diem_tb_he4) < 3.6
        ]
    elif gpa_filter == "TB":  # < 3.2
        sinh_vien_chua_gan = [
            hs for hs in sinh_vien_chua_gan
            if getattr(hs, "diem_dau_vao", None) and getattr(hs.diem_dau_vao, "diem_tb_he4", 0) and float(hs.diem_dau_vao.diem_tb_he4) < 3.2
        ]

    # 4. Danh sách Giảng viên và danh sách sinh viên được gán tương ứng
    qs_giang_vien = giang_vien.objects.filter(
        khoa=dot_obj.khoa
    ).select_related("nguoi_dung", "bo_mon").order_by("nguoi_dung__ho_ten")

    if bo_mon_filter:
        qs_giang_vien = qs_giang_vien.filter(bo_mon_id=bo_mon_filter)

    danh_sach_gv_cards = []
    gv_gpa_averages = []
    gv_day_tai_count = 0

    # Gom các dòng phân công theo giảng viên
    dong_theo_gv = {}
    for dong in cac_dong_phan_cong:
        if dong.trang_thai != PhanCongHuongDanTrangThai.TU_CHOI:
            dong_theo_gv.setdefault(dong.giang_vien_id, []).append(dong)

    for gv in qs_giang_vien:
        assigned_rows = dong_theo_gv.get(gv.id, [])
        so_luong_hien_tai = len(assigned_rows)
        if so_luong_hien_tai >= max_sv_per_gv:
            gv_day_tai_count += 1

        con_lai = max(0, max_sv_per_gv - so_luong_hien_tai)
        phan_tram_tai = min(100, int((so_luong_hien_tai / max_sv_per_gv) * 100)) if max_sv_per_gv > 0 else 0

        # Tính GPA trung bình của nhóm SV của giảng viên này (dành cho Trưởng khoa đánh giá độ lệch chuẩn)
        gpas = []
        for r in assigned_rows:
            ddv = getattr(r.ho_so, "diem_dau_vao", None)
            if ddv and ddv.diem_tb_he4 is not None:
                gpas.append(float(ddv.diem_tb_he4))
        avg_gpa = round(sum(gpas) / len(gpas), 2) if gpas else None
        if avg_gpa is not None:
            gv_gpa_averages.append(avg_gpa)

        danh_sach_gv_cards.append({
            "giang_vien": gv,
            "so_luong_hien_tai": so_luong_hien_tai,
            "so_toi_da": max_sv_per_gv,
            "con_lai": con_lai,
            "phan_tram_tai": phan_tram_tai,
            "avg_gpa": avg_gpa,
            "cac_phan_cong": assigned_rows,
        })

    # 5. Tính độ lệch chuẩn Snake-draft nếu có dữ liệu
    std_dev_gpa = None
    if len(gv_gpa_averages) >= 2:
        mean_gpa = sum(gv_gpa_averages) / len(gv_gpa_averages)
        variance = sum((x - mean_gpa) ** 2 for x in gv_gpa_averages) / len(gv_gpa_averages)
        std_dev_gpa = round(math.sqrt(variance), 2)

    tong_gv_khoa = giang_vien.objects.filter(khoa=dot_obj.khoa).count()
    tong_da_gan = len(ho_so_da_gan_map)
    tong_chua_gan = tong_so_sinh_vien - tong_da_gan
    tong_suc_chua = tong_gv_khoa * max_sv_per_gv
    tong_chi_tieu_con_lai = max(0, tong_suc_chua - tong_da_gan)

    # Danh sách các bộ môn phục vụ lọc
    danh_sach_bo_mon = list(bo_mon.objects.filter(khoa=dot_obj.khoa))

    # Đếm số lượng theo nhóm GPA cho badge bộ lọc
    count_gioi = 0
    count_kha = 0
    count_tb = 0
    for hs in danh_sach_sinh_vien_tong:
        if hs.id not in ho_so_da_gan_map:
            ddv = getattr(hs, "diem_dau_vao", None)
            if ddv and ddv.diem_tb_he4:
                val = float(ddv.diem_tb_he4)
                if val >= 3.6:
                    count_gioi += 1
                elif val >= 3.2:
                    count_kha += 1
                else:
                    count_tb += 1

    return {
        "dot": dot_obj,
        "ban_phan_cong": ban_phan_cong_obj,
        "sinh_vien_chua_gan": sinh_vien_chua_gan,
        "danh_sach_gv_cards": danh_sach_gv_cards,
        "danh_sach_bo_mon": danh_sach_bo_mon,
        "kpi": {
            "tong_sinh_vien": tong_so_sinh_vien,
            "da_gan": tong_da_gan,
            "chua_gan": tong_chua_gan,
            "tong_giang_vien": tong_gv_khoa,
            "gv_day_tai": gv_day_tai_count,
            "chi_tieu_con_lai": tong_chi_tieu_con_lai,
            "std_dev_gpa": std_dev_gpa,
        },
        "counts": {
            "tat_ca": tong_chua_gan,
            "gioi": count_gioi,
            "kha": count_kha,
            "tb": count_tb,
        },
        "filters": {
            "bo_mon_id": bo_mon_filter,
            "gpa": gpa_filter,
            "q": search_query or "",
        }
    }


def lay_danh_sach_xac_nhan_cho_giang_vien(giang_vien_id: int, dot_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Lấy danh sách sinh viên được phân công cho một giảng viên xác nhận (UC10).
    LƯU Ý BẢO MẬT: TUYỆT ĐỐI KHÔNG TRUYỀN DIEM_DAU_VAO RA GIAO DIỆN GIẢNG VIÊN.
    """
    gv = giang_vien.objects.select_related("nguoi_dung", "khoa", "bo_mon").filter(id=giang_vien_id).first()
    if not gv:
        raise ValueError("Không tìm thấy thông tin giảng viên!")

    dot_obj = lay_dot_phan_cong(dot_id)
    if not dot_obj:
        return {"giang_vien": gv, "dot": None, "danh_sach_phan_cong": [], "kpi": {}}

    bpc = ban_phan_cong.objects.filter(dot=dot_obj).order_by("-id").first()
    if not bpc:
        return {"giang_vien": gv, "dot": dot_obj, "ban_phan_cong": None, "danh_sach_phan_cong": [], "kpi": {}}

    # Lấy các dòng phân công của GV này
    qs = phan_cong_huong_dan.objects.filter(
        ban_phan_cong=bpc,
        giang_vien=gv
    ).select_related(
        "ho_so__sinh_vien__nguoi_dung"
    ).order_by("ho_so__sinh_vien__ma_sinh_vien")

    danh_sach = list(qs)
    cho_xac_nhan_count = sum(1 for d in danh_sach if d.trang_thai == PhanCongHuongDanTrangThai.CHO_XAC_NHAN)
    dong_y_count = sum(1 for d in danh_sach if d.trang_thai == PhanCongHuongDanTrangThai.DONG_Y)
    tu_choi_count = sum(1 for d in danh_sach if d.trang_thai == PhanCongHuongDanTrangThai.TU_CHOI)

    return {
        "giang_vien": gv,
        "dot": dot_obj,
        "ban_phan_cong": bpc,
        "danh_sach_phan_cong": danh_sach,
        "kpi": {
            "tong_so": len(danh_sach),
            "cho_xac_nhan": cho_xac_nhan_count,
            "da_dong_y": dong_y_count,
            "da_tu_choi": tu_choi_count,
        }
    }
