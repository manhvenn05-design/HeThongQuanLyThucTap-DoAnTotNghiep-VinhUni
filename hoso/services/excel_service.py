"""
Dịch vụ xử lý file Excel danh sách sinh viên và đồng bộ điểm USMART (UC04, UC05, UC06).
"""
import os
import openpyxl
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from core.constants import (
    LanNhapTrangThai,
    DongNhapTrangThai,
    HoSoTrangThai,
    LoaiNguoiDung,
    NguonDiemDauVao,
    TrangThaiLayDiem,
)
from accounts.models import nguoi_dung
from organization.models import sinh_vien
from hoso.models import (
    lan_nhap_danh_sach,
    dong_nhap_danh_sach,
    ho_so,
    diem_dau_vao,
    lan_lay_diem,
)
from hethong.models import nhat_ky_he_thong
from integrations.usmart.mock import usmart_client


@transaction.atomic
def boc_tach_file_excel(dot_obj, nguoi_tai, file_obj):
    """
    Tải và bóc tách file Excel danh sách sinh viên do Phòng Đào tạo gửi (UC04, UC05).
    Tạo bản ghi xem trước, chưa nạp chính thức vào ho_so.
    """
    # 1. Lưu file ra đĩa
    upload_dir = os.path.join(settings.BASE_DIR, "media", "excel_imports")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{timezone.now().strftime('%Y%m%d_%H%M%S')}_{file_obj.name}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb+") as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)

    # 2. Tạo bản ghi lần nhập ở trạng thái XEM_TRUOC
    lan_nhap = lan_nhap_danh_sach.objects.create(
        dot=dot_obj,
        nguoi_tai=nguoi_tai,
        ten_tep=file_obj.name,
        duong_dan=file_path,
        trang_thai=LanNhapTrangThai.XEM_TRUOC,
    )

    # 3. Đọc dữ liệu bằng openpyxl
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active

    seen_mssv = set()
    dong_hop_le = 0
    dong_loi = 0
    total_rows = 0

    # Tìm dòng tiêu đề (Header row)
    header_row_idx = 1
    col_mssv = None
    col_hoten = None
    col_lop = None
    col_diem = None

    for r in range(1, min(10, sheet.max_row + 1)):
        row_vals = [str(sheet.cell(r, c).value or "").strip().lower() for c in range(1, sheet.max_column + 1)]
        for idx, val in enumerate(row_vals, start=1):
            if any(k in val for k in ["mssv", "mã sv", "mã sinh viên", "mã số"]):
                col_mssv = idx
                header_row_idx = r
            elif any(k in val for k in ["họ tên", "họ và tên", "tên sinh viên"]):
                col_hoten = idx
            elif any(k in val for k in ["lớp", "lớp sinh hoạt"]):
                col_lop = idx
            elif any(k in val for k in ["điểm", "gpa", "điểm tb"]):
                col_diem = idx
        if col_mssv:
            break

    # Nếu không tìm thấy header rõ ràng, mặc định cột 2 là MSSV, cột 3 là Họ tên, cột 4 là Lớp
    if not col_mssv:
        col_mssv = 2
        col_hoten = 3
        col_lop = 4
        header_row_idx = 1

    # Bóc tách từng dòng dữ liệu
    for row_idx in range(header_row_idx + 1, sheet.max_row + 1):
        mssv_raw = sheet.cell(row_idx, col_mssv).value if col_mssv else None
        if mssv_raw is None or str(mssv_raw).strip() == "":
            continue  # Bỏ qua dòng trống

        total_rows += 1
        mssv = str(mssv_raw).strip().upper()
        ho_ten = str(sheet.cell(row_idx, col_hoten).value or "").strip() if col_hoten else ""
        lop = str(sheet.cell(row_idx, col_lop).value or "").strip() if col_lop else ""
        diem_val = sheet.cell(row_idx, col_diem).value if col_diem else None
        diem_tb = None
        if diem_val is not None:
            try:
                diem_tb = float(diem_val)
            except (ValueError, TypeError):
                diem_tb = None

        # Kiểm tra tính hợp lệ
        trang_thai_dong = DongNhapTrangThai.HOP_LE
        loi_msg = []

        if len(mssv) < 4:
            trang_thai_dong = DongNhapTrangThai.LOI
            loi_msg.append("Mã sinh viên quá ngắn hoặc không đúng định dạng")

        if mssv in seen_mssv:
            trang_thai_dong = DongNhapTrangThai.TRUNG
            loi_msg.append("Trùng lặp MSSV với dòng trước trong cùng file")
        else:
            seen_mssv.add(mssv)

        # Kiểm tra đã có hồ sơ trong đợt này chưa
        if ho_so.objects.filter(dot=dot_obj, sinh_vien__ma_sinh_vien=mssv).exists():
            trang_thai_dong = DongNhapTrangThai.TRUNG
            loi_msg.append("Sinh viên đã có hồ sơ trong đợt này")

        if trang_thai_dong == DongNhapTrangThai.HOP_LE:
            dong_hop_le += 1
        else:
            dong_loi += 1

        dong_nhap_danh_sach.objects.create(
            lan_nhap=lan_nhap,
            so_dong=row_idx,
            ma_sinh_vien=mssv,
            ho_ten=ho_ten or None,
            lop=lop or None,
            diem_tb=diem_tb,
            trang_thai_dong=trang_thai_dong,
            loi="; ".join(loi_msg) if loi_msg else None,
        )

    # Cập nhật số lượng
    lan_nhap.tong_dong = total_rows
    lan_nhap.dong_hop_le = dong_hop_le
    lan_nhap.dong_loi = dong_loi
    lan_nhap.save(update_fields=["tong_dong", "dong_hop_le", "dong_loi"])

    return lan_nhap


@transaction.atomic
def xac_nhan_nhap_danh_sach(lan_nhap_obj, nguoi_thuc_hien, ip_address=None):
    """
    Xác nhận danh sách bóc tách (UC05).
    Chỉ nạp các dòng HOP_LE vào hệ thống: tạo tài khoản, sinh_vien, và ho_so (TRONG_DANH_SACH).
    """
    if lan_nhap_obj.trang_thai != LanNhapTrangThai.XEM_TRUOC:
        raise ValueError("Lần nhập này đã được xác nhận hoặc đã hủy trước đó!")

    dot_obj = lan_nhap_obj.dot
    khoa_obj = dot_obj.khoa
    cac_dong_hop_le = lan_nhap_obj.cac_dong_boc_tach.filter(trang_thai_dong=DongNhapTrangThai.HOP_LE)

    tao_moi_count = 0
    for dong in cac_dong_hop_le:
        mssv = dong.ma_sinh_vien.strip().upper()
        ho_ten = dong.ho_ten or f"Sinh viên {mssv}"
        lop = dong.lop or ""

        # 1. Tìm hoặc tạo tài khoản người dùng
        nd, _ = nguoi_dung.objects.get_or_create(
            ma_dinh_danh_cong=mssv,
            defaults={
                "ho_ten": ho_ten,
                "email": f"{mssv.lower()}@vinhuni.edu.vn",
                "loai_nguoi_dung": LoaiNguoiDung.SINH_VIEN,
            }
        )

        # 2. Tìm hoặc tạo sinh viên
        sv, _ = sinh_vien.objects.get_or_create(
            nguoi_dung=nd,
            defaults={
                "ma_sinh_vien": mssv,
                "lop": lop,
                "khoa": khoa_obj,
            }
        )
        if lop and not sv.lop:
            sv.lop = lop
            sv.save(update_fields=["lop"])

        # 3. Tạo hồ sơ chính thức (trạng thái TRONG_DANH_SACH)
        hs, created = ho_so.objects.get_or_create(
            dot=dot_obj,
            sinh_vien=sv,
            defaults={
                "trang_thai": HoSoTrangThai.TRONG_DANH_SACH,
            }
        )
        if created:
            tao_moi_count += 1
            # Nếu trong file có sẵn điểm TB dự phòng
            if dong.diem_tb is not None:
                diem_dau_vao.objects.get_or_create(
                    ho_so=hs,
                    defaults={
                        "diem_tb_he4": dong.diem_tb,
                        "nguon": NguonDiemDauVao.FILE,
                        "ngay_lay": timezone.now(),
                    }
                )

    # Đổi trạng thái lần nhập sang DA_XAC_NHAN
    lan_nhap_obj.trang_thai = LanNhapTrangThai.DA_XAC_NHAN
    lan_nhap_obj.save(update_fields=["trang_thai"])

    # Ghi nhật ký
    nhat_ky_he_thong.objects.create(
        nguoi_thuc_hien=nguoi_thuc_hien,
        hanh_dong="XAC_NHAN_DANH_SACH_SINH_VIEN",
        doi_tuong_loai="lan_nhap_danh_sach",
        doi_tuong_id=lan_nhap_obj.id,
        mo_ta=f"Xác nhận danh sách file {lan_nhap_obj.ten_tep}: Tạo mới {tao_moi_count} hồ sơ sinh viên vào đợt {dot_obj.ma_dot}",
        dia_chi_ip=ip_address,
        thoi_gian=timezone.now()
    )

    return tao_moi_count


@transaction.atomic
def dong_bo_diem_usmart(dot_obj, nguoi_thuc_hien, ip_address=None):
    """
    Đồng bộ điểm trung bình tích lũy hệ 4 từ USMART vào bảng diem_dau_vao (UC06).
    Chỉ Trưởng khoa được phép gọi hàm này.
    """
    danh_sach_hs = ho_so.objects.filter(dot=dot_obj).select_related("sinh_vien")
    if not danh_sach_hs.exists():
        raise ValueError("Đợt chưa có hồ sơ nào để đồng bộ điểm!")

    mssv_list = [hs.sinh_vien.ma_sinh_vien for hs in danh_sach_hs]
    ket_qua_usmart = usmart_client.lay_diem_tich_luy_hang_loat(mssv_list)

    so_co_diem = 0
    so_thieu = 0

    for hs in danh_sach_hs:
        mssv = hs.sinh_vien.ma_sinh_vien.upper()
        data = ket_qua_usmart.get(mssv)

        if data and data.get("diem_tb_he4") is not None:
            so_co_diem += 1
            diem_dau_vao.objects.update_or_create(
                ho_so=hs,
                defaults={
                    "diem_tb_he4": data["diem_tb_he4"],
                    "tin_chi_tich_luy": data.get("tin_chi_tich_luy"),
                    "nguon": NguonDiemDauVao.USMART,
                    "ngay_lay": timezone.now(),
                }
            )
        else:
            so_thieu += 1
            diem_dau_vao.objects.update_or_create(
                ho_so=hs,
                defaults={
                    "diem_tb_he4": None,
                    "tin_chi_tich_luy": None,
                    "nguon": NguonDiemDauVao.KHONG_CO,
                    "ngay_lay": timezone.now(),
                }
            )

    # Ghi nhận lần lấy điểm
    trang_thai_lay = TrangThaiLayDiem.THANH_CONG if so_thieu == 0 else (
        TrangThaiLayDiem.MOT_PHAN if so_co_diem > 0 else TrangThaiLayDiem.LOI
    )
    lan_lay_diem.objects.create(
        dot=dot_obj,
        nguoi_thuc_hien=nguoi_thuc_hien,
        nguon="USMART",
        so_sv_co_diem=so_co_diem,
        so_sv_thieu=so_thieu,
        trang_thai=trang_thai_lay,
        ngay_lay=timezone.now()
    )

    # Ghi nhật ký hệ thống (không ghi điểm số)
    nhat_ky_he_thong.objects.create(
        nguoi_thuc_hien=nguoi_thuc_hien,
        hanh_dong="DONG_BO_DIEM_USMART",
        doi_tuong_loai="dot",
        doi_tuong_id=dot_obj.id,
        mo_ta=f"Đồng bộ điểm USMART cho đợt {dot_obj.ma_dot}: {so_co_diem} có điểm, {so_thieu} thiếu điểm.",
        dia_chi_ip=ip_address,
        thoi_gian=timezone.now()
    )

    return {"so_co_diem": so_co_diem, "so_thieu": so_thieu}
