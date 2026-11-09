from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from dots.models import dot
from accounts.models import nguoi_dung
from hoso.models import ho_so, lan_nhap_danh_sach, dong_nhap_danh_sach
from hoso.services.excel_service import (
    boc_tach_file_excel,
    xac_nhan_nhap_danh_sach,
    dong_bo_diem_usmart,
)
from hoso.selectors import (
    get_hoso_queryset_for_dot,
    get_hoso_statistics_for_dot,
    get_distinct_classes_for_dot,
    get_dot_milestones_and_weights,
)
from core.state import chuyen_trang_thai_dot, StateTransitionError
from core.constants import DotTrangThai


def get_default_truong_khoa():
    """Lấy tài khoản Trưởng khoa demo (TS. Nguyễn Văn An)"""
    return nguoi_dung.objects.filter(ma_dinh_danh_cong="CB_TK01").first()


def sprint1_dashboard(request, dot_id=None):
    """Màn hình Bảng điều khiển chính của Sprint 1 (CHUAN_BI)"""
    if dot_id:
        current_dot = get_object_or_404(dot, id=dot_id)
    else:
        current_dot = dot.objects.filter(trang_thai=DotTrangThai.CHUAN_BI).first()
        if not current_dot:
            current_dot = dot.objects.first()

    if not current_dot:
        return render(request, "sprint1/dashboard.html", {"error": "Chưa có đợt thực tập nào được khởi tạo!"})

    # Bộ lọc tìm kiếm
    q = request.GET.get("q", "").strip()
    lop_filter = request.GET.get("lop", "").strip()

    # Truy vấn qua Selector tầng dữ liệu (Data Access Layer)
    ho_so_qs = get_hoso_queryset_for_dot(current_dot, q=q, lop=lop_filter)
    stats = get_hoso_statistics_for_dot(current_dot)
    danh_sach_lop = get_distinct_classes_for_dot(current_dot)
    moc_thoi_gian, trong_so, cac_lan_nhap = get_dot_milestones_and_weights(current_dot)

    # Phân tách chuyên trách theo Submenu (section: students | upload | milestones)
    active_section = request.GET.get("section", "students")

    context = {
        "current_dot": current_dot,
        "danh_sach_ho_so": ho_so_qs,
        "tong_ho_so": stats["tong_ho_so"],
        "co_diem_count": stats["co_diem_count"],
        "thieu_diem_count": stats["thieu_diem_count"],
        "tyle_diem": stats["tyle_diem"],
        "danh_sach_lop": danh_sach_lop,
        "moc_thoi_gian": moc_thoi_gian,
        "trong_so": trong_so,
        "cac_lan_nhap": cac_lan_nhap,
        "q": q,
        "lop_filter": lop_filter,
        "active_section": active_section,
    }
    return render(request, "sprint1/dashboard.html", context)


def upload_excel_view(request, dot_id):
    """Xử lý tải lên file Excel danh sách sinh viên (UC04)"""
    current_dot = get_object_or_404(dot, id=dot_id)
    if request.method == "POST":
        file_excel = request.FILES.get("file_excel")
        if not file_excel:
            messages.error(request, "Vui lòng chọn file Excel (.xlsx) để tải lên!")
            return redirect("sprint1_dashboard_dot", dot_id=dot_id)

        if not file_excel.name.endswith(('.xlsx', '.xls')):
            messages.error(request, "Định dạng file không hợp lệ! Vui lòng chỉ tải lên file Excel (.xlsx, .xls)")
            return redirect("sprint1_dashboard_dot", dot_id=dot_id)

        try:
            tk = get_default_truong_khoa()
            lan_nhap = boc_tach_file_excel(current_dot, tk, file_excel)
            messages.success(request, f"Đã bóc tách thành công file '{file_excel.name}': {lan_nhap.tong_dong} dòng ({lan_nhap.dong_hop_le} hợp lệ, {lan_nhap.dong_loi} lỗi).")
            return redirect("preview_excel", lan_nhap_id=lan_nhap.id)
        except Exception as e:
            messages.error(request, f"Lỗi khi đọc file Excel: {str(e)}")
            return redirect("sprint1_dashboard_dot", dot_id=dot_id)

    return redirect("sprint1_dashboard_dot", dot_id=dot_id)


def preview_excel_view(request, lan_nhap_id):
    """Màn hình xem trước kết quả bóc tách file Excel (UC05)"""
    lan_nhap = get_object_or_404(lan_nhap_danh_sach, id=lan_nhap_id)
    dong_qs = lan_nhap.cac_dong_boc_tach.all().order_by("so_dong")

    filter_trang_thai = request.GET.get("trang_thai", "")
    if filter_trang_thai:
        dong_qs = dong_qs.filter(trang_thai_dong=filter_trang_thai)

    context = {
        "current_dot": lan_nhap.dot,
        "lan_nhap": lan_nhap,
        "danh_sach_dong": dong_qs,
        "filter_trang_thai": filter_trang_thai,
    }
    return render(request, "sprint1/preview_import.html", context)


def confirm_excel_view(request, lan_nhap_id):
    """Xác nhận nạp các dòng hợp lệ vào đợt (UC05)"""
    lan_nhap = get_object_or_404(lan_nhap_danh_sach, id=lan_nhap_id)
    if request.method == "POST":
        try:
            tk = get_default_truong_khoa()
            count = xac_nhan_nhap_danh_sach(lan_nhap, tk)
            messages.success(request, f"Xác nhận thành công! Đã thêm {count} hồ sơ sinh viên vào đợt.")
        except Exception as e:
            messages.error(request, f"Lỗi khi xác nhận danh sách: {str(e)}")
        return redirect("sprint1_dashboard_dot", dot_id=lan_nhap.dot.id)

    return redirect("preview_excel", lan_nhap_id=lan_nhap_id)


def sync_usmart_view(request, dot_id):
    """Đồng bộ điểm TB tích lũy từ USMART (UC06)"""
    current_dot = get_object_or_404(dot, id=dot_id)
    if request.method == "POST":
        try:
            tk = get_default_truong_khoa()
            res = dong_bo_diem_usmart(current_dot, tk)
            messages.success(
                request,
                f"Đồng bộ USMART hoàn tất: {res['so_co_diem']} sinh viên có điểm, {res['so_thieu']} sinh viên chưa có điểm."
            )
        except Exception as e:
            messages.error(request, f"Lỗi đồng bộ USMART: {str(e)}")

    return redirect("sprint1_dashboard_dot", dot_id=dot_id)


def advance_phase_view(request, dot_id):
    """Chuyển đợt sang bước Phân công hướng dẫn (UC03)"""
    current_dot = get_object_or_404(dot, id=dot_id)
    if request.method == "POST":
        try:
            tk = get_default_truong_khoa()
            chuyen_trang_thai_dot(
                dot_obj=current_dot,
                trang_thai_moi=DotTrangThai.PHAN_CONG,
                nguoi_thuc_hien=tk,
                ly_do="Trưởng khoa duyệt hoàn tất khâu chuẩn bị, chuyển sang phân công GVHD."
            )
            messages.success(request, f"Đã chuyển đợt {current_dot.ma_dot} sang giai đoạn: '2. Phân công hướng dẫn' thành công!")
            return redirect("phancong:dashboard_dot", dot_id=dot_id)
        except StateTransitionError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Lỗi: {str(e)}")

    return redirect("sprint1_dashboard_dot", dot_id=dot_id)
