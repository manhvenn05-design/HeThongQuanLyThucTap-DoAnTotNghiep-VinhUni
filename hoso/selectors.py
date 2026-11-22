"""
Selectors cho app Hoso: Chịu trách nhiệm truy vấn dữ liệu hồ sơ sinh viên,
thống kê và phân quyền theo chuẩn Layered Architecture (GEMINI.md).
"""
from django.db.models import Q
from hoso.models import ho_so


def get_hoso_queryset_for_dot(dot_instance, q="", lop="", status_filter="all"):
    """
    Lấy danh sách hồ sơ sinh viên trong đợt kèm tìm kiếm, lọc lớp và lọc điều kiện tốt nghiệp (UC06).
    - status_filter:
      * 'all': Tất cả hồ sơ
      * 'eligible': Đủ điều kiện (tín chỉ >= 110 và điểm TB >= 2.0)
      * 'ineligible': Chưa đủ điều kiện (tín chỉ < 110 hoặc thiếu điểm)
    """
    ho_so_qs = ho_so.objects.filter(dot=dot_instance).select_related(
        "sinh_vien", "sinh_vien__nguoi_dung", "diem_dau_vao"
    ).order_by("sinh_vien__lop", "sinh_vien__ma_sinh_vien")

    if q:
        ho_so_qs = ho_so_qs.filter(
            Q(sinh_vien__ma_sinh_vien__icontains=q) |
            Q(sinh_vien__nguoi_dung__ho_ten__icontains=q)
        )
    if lop:
        ho_so_qs = ho_so_qs.filter(sinh_vien__lop=lop)

    if status_filter == "eligible":
        ho_so_qs = ho_so_qs.filter(
            diem_dau_vao__tin_chi_tich_luy__gte=110,
            diem_dau_vao__diem_tb_he4__gte=2.0
        )
    elif status_filter == "ineligible":
        ho_so_qs = ho_so_qs.filter(
            Q(diem_dau_vao__isnull=True) |
            Q(diem_dau_vao__tin_chi_tich_luy__lt=110) |
            Q(diem_dau_vao__tin_chi_tich_luy__isnull=True) |
            Q(diem_dau_vao__diem_tb_he4__lt=2.0) |
            Q(diem_dau_vao__diem_tb_he4__isnull=True)
        )

    return ho_so_qs


def get_hoso_statistics_for_dot(dot_instance):
    """Tính toán thống kê số lượng hồ sơ, tiến độ đồng bộ điểm USMART và điều kiện tốt nghiệp (UC06)."""
    tong_ho_so = ho_so.objects.filter(dot=dot_instance).count()
    co_diem_count = ho_so.objects.filter(dot=dot_instance, diem_dau_vao__diem_tb_he4__isnull=False).count()
    thieu_diem_count = tong_ho_so - co_diem_count
    tyle_diem = round((co_diem_count / tong_ho_so * 100), 1) if tong_ho_so > 0 else 0

    du_dieu_kien_count = ho_so.objects.filter(
        dot=dot_instance,
        diem_dau_vao__tin_chi_tich_luy__gte=110,
        diem_dau_vao__diem_tb_he4__gte=2.0
    ).count()
    chua_du_dieu_kien_count = tong_ho_so - du_dieu_kien_count
    tyle_du_dieu_kien = round((du_dieu_kien_count / tong_ho_so * 100), 1) if tong_ho_so > 0 else 0

    return {
        "tong_ho_so": tong_ho_so,
        "co_diem_count": co_diem_count,
        "thieu_diem_count": thieu_diem_count,
        "tyle_diem": tyle_diem,
        "du_dieu_kien_count": du_dieu_kien_count,
        "chua_du_dieu_kien_count": chua_du_dieu_kien_count,
        "tyle_du_dieu_kien": tyle_du_dieu_kien,
    }


def get_distinct_classes_for_dot(dot_instance):
    """Lấy danh sách các lớp học có sinh viên tham gia đợt."""
    danh_sach_lop = ho_so.objects.filter(dot=dot_instance).values_list("sinh_vien__lop", flat=True).distinct()
    return sorted([l for l in danh_sach_lop if l])


def get_dot_milestones_and_weights(dot_instance):
    """Lấy các mốc thời gian và trọng số đánh giá của đợt."""
    moc_thoi_gian = dot_instance.cac_moc_thoi_gian.all()
    trong_so = dot_instance.cac_trong_so.all()
    cac_lan_nhap = dot_instance.cac_lan_nhap_danh_sach.order_by("-ngay_tai")[:5]

    return moc_thoi_gian, trong_so, cac_lan_nhap
