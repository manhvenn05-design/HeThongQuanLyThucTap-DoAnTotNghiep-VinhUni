"""
Dịch vụ Phân công hướng dẫn & Thuật toán chia đều Snake Draft (UC07, UC08, UC09, UC10).
Tuân thủ 100% thuật toán mục 8.1 và ma trận quyền trong PROJECT_SPEC.
"""
import random
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from core.constants import (
    DotTrangThai,
    HoSoTrangThai,
    BanPhanCongTrangThai,
    PhanCongHuongDanTrangThai,
)
from dots.models import dot
from organization.models import giang_vien
from hoso.models import ho_so
from phancong.models import ban_phan_cong, phan_cong_huong_dan
from hethong.models import thong_bao, nhat_ky_he_thong
from core.state import chuyen_trang_thai_ho_so, chuyen_trang_thai_dot, StateTransitionError


def lay_hoac_tao_ban_phan_cong(dot_obj, nguoi_tao):
    """Lấy hoặc tạo bản phân công nháp cho đợt"""
    bpc = ban_phan_cong.objects.filter(dot=dot_obj).order_by("-id").first()
    if not bpc:
        bpc = ban_phan_cong.objects.create(
            dot=dot_obj,
            nguoi_tao=nguoi_tao,
            trang_thai=BanPhanCongTrangThai.NHAP,
        )
    return bpc


@transaction.atomic
def thuat_toan_snake_draft(dot_obj, ban_phan_cong_obj, nguoi_thuc_hien, ip_address=None):
    """
    Thuật toán gợi ý chia đều sinh viên theo điểm tích lũy GPA (Snake-draft) - Mục 8.1 (UC08).
    Đảm bảo:
    1. Mỗi GVHD nhận số lượng SV gần bằng nhau (chênh nhau <= 1).
    2. Cân bằng học lực: mỗi GV đều có đủ sinh viên giỏi, khá, trung bình.
    3. Tuyệt đối không vượt quá hạn mức so_sv_toi_da_moi_gv.
    """
    # 1. Danh sách giảng viên trong khoa (thứ tự cố định)
    danh_sach_gv = list(giang_vien.objects.filter(khoa=dot_obj.khoa).select_related("nguoi_dung").order_by("id"))
    if not danh_sach_gv:
        raise ValueError("Khoa chưa có giảng viên nào để phân công hướng dẫn!")

    max_sv = dot_obj.so_sv_toi_da_moi_gv

    # 2. Lấy toàn bộ hồ sơ cần phân công trong đợt
    danh_sach_hs = list(ho_so.objects.filter(dot=dot_obj).select_related("sinh_vien", "diem_dau_vao"))
    if not danh_sach_hs:
        raise ValueError("Đợt chưa có hồ sơ sinh viên nào để phân công!")

    # Tính dung lượng còn lại
    tong_cho_trong = len(danh_sach_gv) * max_sv
    if len(danh_sach_hs) > tong_cho_trong:
        raise ValueError(f"Thiếu chỉ tiêu: Cần phân bổ {len(danh_sach_hs)} SV, nhưng khoa chỉ có {tong_cho_trong} chỗ tối đa!")

    # 3. Tách H_co_diem và H_chua_co_diem theo mục 8.1
    h_co_diem = []
    h_chua_diem = []

    for hs in danh_sach_hs:
        diem = getattr(hs, "diem_dau_vao", None)
        if diem and diem.diem_tb_he4 is not None:
            h_co_diem.append((float(diem.diem_tb_he4), diem.tin_chi_tich_luy or 0, hs.sinh_vien.ma_sinh_vien, hs))
        else:
            h_chua_diem.append(hs)

    # 4. Sắp xếp H_co_diem giảm dần theo điểm TB hệ 4 (hòa thì theo tín chỉ, rồi mã SV)
    h_co_diem.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    sorted_hs_co_diem = [item[3] for item in h_co_diem]

    # Map số lượng đã nhận của mỗi giảng viên
    gv_assigned = {gv.id: [] for gv in danh_sach_gv}
    num_gv = len(danh_sach_gv)

    # 5. Phân bổ vòng kiểu rắn (Snake-draft) cho nhóm có điểm
    round_idx = 0
    curr_hs_idx = 0
    total_co_diem = len(sorted_hs_co_diem)

    while curr_hs_idx < total_co_diem:
        # Vòng chẵn đi xuôi: 0 -> num_gv-1; Vòng lẻ đi ngược: num_gv-1 -> 0
        gv_indices = range(num_gv) if round_idx % 2 == 0 else range(num_gv - 1, -1, -1)
        for g_idx in gv_indices:
            if curr_hs_idx >= total_co_diem:
                break
            gv = danh_sach_gv[g_idx]
            if len(gv_assigned[gv.id]) < max_sv:
                gv_assigned[gv.id].append(sorted_hs_co_diem[curr_hs_idx])
                curr_hs_idx += 1
        round_idx += 1

    # 6. Nhóm chưa có điểm: xáo trộn ngẫu nhiên (seed cố định), gán lần lượt cho GV ít SV nhất
    random.seed(42)
    random.shuffle(h_chua_diem)
    for hs in h_chua_diem:
        # Tìm GV có ít SV nhất và còn chỉ tiêu
        gv_min = min(danh_sach_gv, key=lambda g: len(gv_assigned[g.id]))
        if len(gv_assigned[gv_min.id]) < max_sv:
            gv_assigned[gv_min.id].append(hs)

    # 7. Lưu kết quả vào bảng phan_cong_huong_dan (trạng thái NHAP, la_goi_y = TRUE)
    # Xóa các dòng phân công nháp cũ nếu có
    phan_cong_huong_dan.objects.filter(ban_phan_cong=ban_phan_cong_obj, trang_thai=PhanCongHuongDanTrangThai.NHAP).delete()

    created_count = 0
    for gv in danh_sach_gv:
        for hs in gv_assigned[gv.id]:
            phan_cong_huong_dan.objects.create(
                ban_phan_cong=ban_phan_cong_obj,
                ho_so=hs,
                giang_vien=gv,
                trang_thai=PhanCongHuongDanTrangThai.NHAP,
                la_goi_y=True,
            )
            created_count += 1

    # Ghi nhật ký
    nhat_ky_he_thong.objects.create(
        nguoi_thuc_hien=nguoi_thuc_hien,
        hanh_dong="CHAY_THUAT_TOAN_SNAKE_DRAFT",
        doi_tuong_loai="ban_phan_cong",
        doi_tuong_id=ban_phan_cong_obj.id,
        mo_ta=f"Chạy thuật toán Snake-draft chia đều {created_count} sinh viên cho {len(danh_sach_gv)} giảng viên.",
        dia_chi_ip=ip_address,
        thoi_gian=timezone.now()
    )

    return created_count


@transaction.atomic
def gan_sinh_vien_thu_cong(ban_phan_cong_obj, ho_so_id, giang_vien_id, nguoi_thuc_hien, ip_address=None):
    """Trưởng khoa chỉnh tay gán hồ sơ cho một giảng viên (la_goi_y = FALSE)"""
    hs = ho_so.objects.get(id=ho_so_id, dot=ban_phan_cong_obj.dot)
    gv = giang_vien.objects.get(id=giang_vien_id, khoa=ban_phan_cong_obj.dot.khoa)

    # Kiểm tra hạn mức
    so_luong_hien_tai = phan_cong_huong_dan.objects.filter(
        ban_phan_cong=ban_phan_cong_obj,
        giang_vien=gv
    ).exclude(trang_thai=PhanCongHuongDanTrangThai.TU_CHOI).count()

    if so_luong_hien_tai >= ban_phan_cong_obj.dot.so_sv_toi_da_moi_gv:
        raise ValueError(f"Giảng viên {gv.nguoi_dung.ho_ten} đã đạt hạn mức tối đa ({so_luong_hien_tai}/{ban_phan_cong_obj.dot.so_sv_toi_da_moi_gv})!")

    # Cập nhật hoặc tạo dòng phân công
    pc, _ = phan_cong_huong_dan.objects.update_or_create(
        ban_phan_cong=ban_phan_cong_obj,
        ho_so=hs,
        defaults={
            "giang_vien": gv,
            "trang_thai": PhanCongHuongDanTrangThai.NHAP,
            "la_goi_y": False,  # Chỉnh tay
            "ly_do_tu_choi": None,
        }
    )

    nhat_ky_he_thong.objects.create(
        nguoi_thuc_hien=nguoi_thuc_hien,
        hanh_dong="GAN_GVHD_THU_CONG",
        doi_tuong_loai="phan_cong_huong_dan",
        doi_tuong_id=pc.id,
        mo_ta=f"Gán hồ sơ SV {hs.sinh_vien.ma_sinh_vien} cho GV {gv.nguoi_dung.ho_ten}",
        dia_chi_ip=ip_address,
        thoi_gian=timezone.now()
    )
    return pc


@transaction.atomic
def xoa_phan_cong_thu_cong(ban_phan_cong_obj, ho_so_id, nguoi_thuc_hien, ip_address=None):
    """Xóa phân công của một sinh viên để trả về danh sách chưa gán"""
    deleted_count, _ = phan_cong_huong_dan.objects.filter(
        ban_phan_cong=ban_phan_cong_obj,
        ho_so_id=ho_so_id
    ).delete()
    return deleted_count


@transaction.atomic
def gui_ban_phan_cong_cho_giang_vien(ban_phan_cong_obj, nguoi_thuc_hien, ip_address=None):
    """
    Trưởng khoa gửi bản phân công cho các GVHD xác nhận (UC07).
    Chuyển trạng thái bản phân công -> DA_GUI.
    Chuyển dòng phân công -> CHO_XAC_NHAN.
    Chuyển trạng thái ho_so -> CHO_XAC_NHAN.
    Gửi thông báo tới từng GVHD.
    """
    dot_obj = ban_phan_cong_obj.dot
    tong_hs = ho_so.objects.filter(dot=dot_obj).count()
    da_phan_cong = phan_cong_huong_dan.objects.filter(ban_phan_cong=ban_phan_cong_obj).count()

    if da_phan_cong < tong_hs:
        raise ValueError(f"Chưa phân công đủ sinh viên: Còn {tong_hs - da_phan_cong} sinh viên chưa có GVHD!")

    # Cập nhật bản phân công
    ban_phan_cong_obj.trang_thai = BanPhanCongTrangThai.DA_GUI
    ban_phan_cong_obj.ngay_gui = timezone.now()
    ban_phan_cong_obj.save(update_fields=["trang_thai", "ngay_gui"])

    # Cập nhật từng dòng và hồ sơ
    cac_dong = phan_cong_huong_dan.objects.filter(ban_phan_cong=ban_phan_cong_obj).select_related("ho_so", "giang_vien__nguoi_dung")
    gv_notified = set()

    for d in cac_dong:
        d.trang_thai = PhanCongHuongDanTrangThai.CHO_XAC_NHAN
        d.save(update_fields=["trang_thai"])

        # Chuyển trạng thái ho_so qua core/state.py
        chuyen_trang_thai_ho_so(
            ho_so_obj=d.ho_so,
            trang_thai_moi=HoSoTrangThai.CHO_XAC_NHAN,
            nguoi_thuc_hien=nguoi_thuc_hien,
            ly_do="Trưởng khoa gửi bản phân công hướng dẫn",
            ip_address=ip_address
        )

        gv_notified.add(d.giang_vien)

    # Gửi thông báo đến từng GVHD
    for gv in gv_notified:
        thong_bao.objects.create(
            nguoi_nhan=gv.nguoi_dung,
            tieu_de=f"Xác nhận phân công hướng dẫn: {dot_obj.ten_dot}",
            noi_dung=f"Trưởng khoa đã gửi bản phân công hướng dẫn cho đợt {dot_obj.ma_dot}. Vui lòng kiểm tra và xác nhận tiếp nhận sinh viên.",
            loai="PHAN_CONG",
            duong_dan_dieu_huong=f"/phancong/xac-nhan/{gv.id}/{dot_obj.id}/",
        )

    # Ghi nhật ký
    nhat_ky_he_thong.objects.create(
        nguoi_thuc_hien=nguoi_thuc_hien,
        hanh_dong="GUI_BAN_PHAN_CONG_CHO_GV",
        doi_tuong_loai="ban_phan_cong",
        doi_tuong_id=ban_phan_cong_obj.id,
        mo_ta=f"Gửi bản phân công đợt {dot_obj.ma_dot} cho {len(gv_notified)} giảng viên xác nhận.",
        dia_chi_ip=ip_address,
        thoi_gian=timezone.now()
    )

    return len(gv_notified)


@transaction.atomic
def gv_phan_hoi_phan_cong(phan_cong_obj, dong_y: bool, ly_do="", nguoi_thuc_hien=None, ip_address=None):
    """
    Giảng viên xác nhận hoặc từ chối từng sinh viên (UC10).
    Nếu từ chối: Bắt buộc có lý do -> ho_so quay lại TRONG_DANH_SACH để Trưởng khoa phân lại.
    """
    hs = phan_cong_obj.ho_so
    dot_obj = phan_cong_obj.ban_phan_cong.dot

    if dong_y:
        phan_cong_obj.trang_thai = PhanCongHuongDanTrangThai.DONG_Y
        phan_cong_obj.ngay_phan_hoi = timezone.now()
        phan_cong_obj.save(update_fields=["trang_thai", "ngay_phan_hoi"])
    else:
        if not str(ly_do).strip():
            raise ValueError("Bắt buộc phải nhập lý do từ chối!")
        phan_cong_obj.trang_thai = PhanCongHuongDanTrangThai.TU_CHOI
        phan_cong_obj.ly_do_tu_choi = ly_do.strip()
        phan_cong_obj.ngay_phan_hoi = timezone.now()
        phan_cong_obj.save(update_fields=["trang_thai", "ly_do_tu_choi", "ngay_phan_hoi"])

        # Nhánh quay lại duy nhất theo quy tắc spec: ho_so quay về TRONG_DANH_SACH
        chuyen_trang_thai_ho_so(
            ho_so_obj=hs,
            trang_thai_moi=HoSoTrangThai.TRONG_DANH_SACH,
            nguoi_thuc_hien=nguoi_thuc_hien,
            ly_do=f"GV {phan_cong_obj.giang_vien.nguoi_dung.ho_ten} từ chối: {ly_do}",
            ip_address=ip_address
        )

        # Thông báo cho Trưởng khoa
        tkhoa = dot_obj.nguoi_tao
        thong_bao.objects.create(
            nguoi_nhan=tkhoa,
            tieu_de=f"Giảng viên từ chối tiếp nhận sinh viên ({dot_obj.ma_dot})",
            noi_dung=f"Giảng viên {phan_cong_obj.giang_vien.nguoi_dung.ho_ten} đã từ chối hướng dẫn SV {hs.sinh_vien.ma_sinh_vien} ({hs.sinh_vien.nguoi_dung.ho_ten}). Lý do: {ly_do}",
            loai="PHAN_CONG",
            duong_dan_dieu_huong=f"/phancong/{dot_obj.id}/",
        )

    return phan_cong_obj


@transaction.atomic
def gv_dong_y_tat_ca(ban_phan_cong_obj, giang_vien_obj, nguoi_thuc_hien=None, ip_address=None):
    """Giảng viên bấm nút 'Đồng ý tất cả' danh sách phân công gửi cho mình (UC10)"""
    cac_dong = phan_cong_huong_dan.objects.filter(
        ban_phan_cong=ban_phan_cong_obj,
        giang_vien=giang_vien_obj,
        trang_thai=PhanCongHuongDanTrangThai.CHO_XAC_NHAN
    )
    count = 0
    now = timezone.now()
    for d in cac_dong:
        d.trang_thai = PhanCongHuongDanTrangThai.DONG_Y
        d.ngay_phan_hoi = now
        d.save(update_fields=["trang_thai", "ngay_phan_hoi"])
        count += 1
    return count


@transaction.atomic
def cong_bo_danh_sach_chinh_thuc(ban_phan_cong_obj, nguoi_thuc_hien, ip_address=None):
    """
    Trưởng khoa công bố danh sách phân công chính thức (UC09).
    Điều kiện: Mọi sinh viên đều phải được GVHD đồng ý (DONG_Y).
    Kết quả:
    - ban_phan_cong -> DA_CONG_BO
    - ho_so.giang_vien_huong_dan_id được gán chính thức
    - ho_so -> CHO_CHOT_DE_TAI
    - dot -> CHOT_DE_TAI (chuyển sang Sprint 3)
    - Thông báo cho toàn thể GV và SV
    """
    dot_obj = ban_phan_cong_obj.dot
    cac_dong = phan_cong_huong_dan.objects.filter(ban_phan_cong=ban_phan_cong_obj)

    # Kiểm tra còn dòng nào chưa đồng ý không
    chua_dong_y = cac_dong.exclude(trang_thai=PhanCongHuongDanTrangThai.DONG_Y)
    if chua_dong_y.exists():
        raise ValueError(f"Chưa thể công bố chính thức: Còn {chua_dong_y.count()} phân công chưa được giảng viên đồng ý hoặc bị từ chối!")

    # Cập nhật bản phân công
    ban_phan_cong_obj.trang_thai = BanPhanCongTrangThai.DA_CONG_BO
    ban_phan_cong_obj.ngay_cong_bo = timezone.now()
    ban_phan_cong_obj.save(update_fields=["trang_thai", "ngay_cong_bo"])

    # Cập nhật từng hồ sơ
    for d in cac_dong:
        hs = d.ho_so
        hs.giang_vien_huong_dan = d.giang_vien
        hs.save(update_fields=["giang_vien_huong_dan"])

        # Chuyển trạng thái ho_so sang CHO_CHOT_DE_TAI
        chuyen_trang_thai_ho_so(
            ho_so_obj=hs,
            trang_thai_moi=HoSoTrangThai.CHO_CHOT_DE_TAI,
            nguoi_thuc_hien=nguoi_thuc_hien,
            ly_do="Công bố chính thức danh sách phân công hướng dẫn",
            ip_address=ip_address
        )

        # Thông báo cho sinh viên (UC11)
        thong_bao.objects.create(
            nguoi_nhan=hs.sinh_vien.nguoi_dung,
            tieu_de=f"Công bố GVHD chính thức: {dot_obj.ten_dot}",
            noi_dung=f"Bạn đã được phân công Giảng viên hướng dẫn: {d.giang_vien.nguoi_dung.ho_ten}. Hãy chuẩn bị chọn hoặc đề xuất đề tài.",
            loai="PHAN_CONG",
        )

    # Chuyển trạng thái đợt sang CHOT_DE_TAI qua core/state.py
    chuyen_trang_thai_dot(
        dot_obj=dot_obj,
        trang_thai_moi=DotTrangThai.CHOT_DE_TAI,
        nguoi_thuc_hien=nguoi_thuc_hien,
        ly_do="Công bố phân công chính thức, tự động mở giai đoạn Chọn & Chốt đề tài",
        ip_address=ip_address
    )

    return cac_dong.count()
