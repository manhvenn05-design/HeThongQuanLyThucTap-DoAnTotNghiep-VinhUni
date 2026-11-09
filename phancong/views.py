"""
Views cho Sprint 2: Phân công Hướng dẫn (UC07, UC08, UC09, UC10, UC11).
Phân tầng kiến trúc rõ ràng: View mỏng, chỉ nhận request, gọi Selector/Service, trả về Response.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST, require_http_methods
from django.http import HttpResponse, Http404
from dots.models import dot
from organization.models import giang_vien
from hoso.models import ho_so
from phancong.models import ban_phan_cong, phan_cong_huong_dan
from core.constants import DotTrangThai, BanPhanCongTrangThai, PhanCongHuongDanTrangThai
from phancong.selectors import (
    lay_dot_phan_cong,
    lay_hoac_khoi_tao_ban_phan_cong,
    lay_du_lieu_dashboard_sprint2,
    lay_danh_sach_xac_nhan_cho_giang_vien,
)
from phancong.services.allocation_service import (
    thuat_toan_snake_draft,
    gan_sinh_vien_thu_cong,
    xoa_phan_cong_thu_cong,
    gui_ban_phan_cong_cho_giang_vien,
    gv_phan_hoi_phan_cong,
    gv_dong_y_tat_ca,
    cong_bo_danh_sach_chinh_thuc,
)
from phancong.services.excel_export import xuat_excel_du_thao_phan_cong
from core.state import chuyen_trang_thai_dot, StateTransitionError


def _lay_nguoi_thuc_hien(request, dot_obj):
    """Lấy user thực hiện từ request hoặc fallback người tạo đợt nếu chưa login"""
    if request.user.is_authenticated:
        return request.user
    return dot_obj.nguoi_tao


def sprint2_dashboard_view(request, dot_id=None):
    """Màn hình chính Sprint 2: Bảng điều khiển phân công hướng dẫn (Dành cho Trưởng khoa)"""
    dot_obj = lay_dot_phan_cong(dot_id)
    if not dot_obj:
        messages.error(request, "Chưa có đợt thực tập / đồ án nào trong hệ thống!")
        return redirect("/dots/")

    # Tự động nâng trạng thái từ CHUAN_BI lên PHAN_CONG nếu đợt đã có hồ sơ và đang xem Sprint 2
    if dot_obj.trang_thai == DotTrangThai.CHUAN_BI and dot_obj.cac_ho_so.exists():
        try:
            nguoi_dung = _lay_nguoi_thuc_hien(request, dot_obj)
            chuyen_trang_thai_dot(
                dot_obj=dot_obj,
                trang_thai_moi=DotTrangThai.PHAN_CONG,
                nguoi_thuc_hien=nguoi_dung,
                ly_do="Khởi động Phân công Hướng dẫn"
            )
        except Exception:
            pass

    nguoi_dung = _lay_nguoi_thuc_hien(request, dot_obj)
    bpc = lay_hoac_khoi_tao_ban_phan_cong(dot_obj, nguoi_dung)

    bo_mon_id = request.GET.get("bo_mon")
    bo_mon_id = int(bo_mon_id) if bo_mon_id and bo_mon_id.isdigit() else None
    gpa_filter = request.GET.get("gpa")
    search_query = request.GET.get("q")

    view_mode = request.GET.get("view", "board")

    context_data = lay_du_lieu_dashboard_sprint2(
        dot_obj=dot_obj,
        ban_phan_cong_obj=bpc,
        bo_mon_filter=bo_mon_id,
        gpa_filter=gpa_filter,
        search_query=search_query
    )
    context_data["active_sprint"] = 2
    context_data["current_dot"] = dot_obj
    context_data["view_mode"] = view_mode

    return render(request, "sprint2/dashboard.html", context_data)


@require_POST
def chay_snake_draft_action(request, dot_id):
    """Kích hoạt thuật toán Snake-draft chia đều theo GPA (UC07, UC08)"""
    dot_obj = get_object_or_404(dot, id=dot_id)
    nguoi_dung = _lay_nguoi_thuc_hien(request, dot_obj)
    bpc = lay_hoac_khoi_tao_ban_phan_cong(dot_obj, nguoi_dung)

    if bpc.trang_thai == BanPhanCongTrangThai.DA_CONG_BO:
        messages.error(request, "Bản phân công đã được công bố chính thức, không thể phân bổ lại!")
        return redirect("phancong:dashboard_dot", dot_id=dot_id)

    try:
        ip = request.META.get("REMOTE_ADDR")
        so_luong = thuat_toan_snake_draft(dot_obj, bpc, nguoi_dung, ip)
        messages.success(request, f"Đã áp dụng thành công thuật toán Snake-draft chia đều {so_luong} sinh viên cho các giảng viên!")
    except Exception as e:
        messages.error(request, f"Lỗi khi chạy thuật toán phân công: {str(e)}")

    return redirect("phancong:dashboard_dot", dot_id=dot_id)


@require_POST
def gan_thu_cong_action(request, dot_id):
    """Trưởng khoa ghép thủ công một sinh viên cho giảng viên"""
    dot_obj = get_object_or_404(dot, id=dot_id)
    nguoi_dung = _lay_nguoi_thuc_hien(request, dot_obj)
    bpc = lay_hoac_khoi_tao_ban_phan_cong(dot_obj, nguoi_dung)

    ho_so_id = request.POST.get("ho_so_id")
    giang_vien_id = request.POST.get("giang_vien_id")

    if not ho_so_id or not giang_vien_id:
        messages.error(request, "Thiếu thông tin sinh viên hoặc giảng viên cần gán!")
        return redirect("phancong:dashboard_dot", dot_id=dot_id)

    try:
        ip = request.META.get("REMOTE_ADDR")
        pc = gan_sinh_vien_thu_cong(bpc, int(ho_so_id), int(giang_vien_id), nguoi_dung, ip)
        messages.success(request, f"Đã gán thành công sinh viên {pc.ho_so.sinh_vien.nguoi_dung.ho_ten} cho {pc.giang_vien.nguoi_dung.ho_ten}!")
    except Exception as e:
        messages.error(request, f"Không thể gán thủ công: {str(e)}")

    return redirect("phancong:dashboard_dot", dot_id=dot_id)


@require_POST
def xoa_phan_cong_action(request, dot_id, ho_so_id):
    """Gỡ sinh viên khỏi giảng viên để trả về danh sách chưa phân công"""
    dot_obj = get_object_or_404(dot, id=dot_id)
    nguoi_dung = _lay_nguoi_thuc_hien(request, dot_obj)
    bpc = lay_hoac_khoi_tao_ban_phan_cong(dot_obj, nguoi_dung)

    if bpc.trang_thai == BanPhanCongTrangThai.DA_CONG_BO:
        messages.error(request, "Danh sách đã công bố chính thức, không thể gỡ phân công!")
        return redirect("phancong:dashboard_dot", dot_id=dot_id)

    try:
        ip = request.META.get("REMOTE_ADDR")
        xoa_phan_cong_thu_cong(bpc, ho_so_id, nguoi_dung, ip)
        messages.success(request, "Đã gỡ phân công thành công, sinh viên đã quay lại danh sách chưa gán.")
    except Exception as e:
        messages.error(request, f"Lỗi khi gỡ phân công: {str(e)}")

    return redirect("phancong:dashboard_dot", dot_id=dot_id)


@require_POST
def gui_ban_phan_cong_action(request, dot_id):
    """Trưởng khoa gửi bản phân công cho toàn thể GVHD xác nhận (UC07)"""
    dot_obj = get_object_or_404(dot, id=dot_id)
    nguoi_dung = _lay_nguoi_thuc_hien(request, dot_obj)
    bpc = lay_hoac_khoi_tao_ban_phan_cong(dot_obj, nguoi_dung)

    try:
        ip = request.META.get("REMOTE_ADDR")
        so_gv = gui_ban_phan_cong_cho_giang_vien(bpc, nguoi_dung, ip)
        messages.success(request, f"Đã gửi bản phân công thành công tới {so_gv} giảng viên để xác nhận tiếp nhận sinh viên!")
    except Exception as e:
        messages.error(request, f"Không thể gửi bản phân công: {str(e)}")

    return redirect("phancong:dashboard_dot", dot_id=dot_id)


@require_POST
def cong_bo_chinh_thuc_action(request, dot_id):
    """Trưởng khoa công bố danh sách phân công chính thức (UC09)"""
    dot_obj = get_object_or_404(dot, id=dot_id)
    nguoi_dung = _lay_nguoi_thuc_hien(request, dot_obj)
    bpc = lay_hoac_khoi_tao_ban_phan_cong(dot_obj, nguoi_dung)

    try:
        ip = request.META.get("REMOTE_ADDR")
        so_sv = cong_bo_danh_sach_chinh_thuc(bpc, nguoi_dung, ip)
        messages.success(request, f"Đã công bố chính thức danh sách phân công {so_sv} sinh viên! Hệ thống đã tự động chuyển sang Giai đoạn 3 (Chốt đề tài).")
    except Exception as e:
        messages.error(request, f"Chưa thể công bố chính thức: {str(e)}")

    return redirect("phancong:dashboard_dot", dot_id=dot_id)


def xuat_excel_du_thao_action(request, dot_id):
    """Tải file Excel dự thảo phân công hướng dẫn (UC08)"""
    dot_obj = get_object_or_404(dot, id=dot_id)
    nguoi_dung = _lay_nguoi_thuc_hien(request, dot_obj)
    bpc = lay_hoac_khoi_tao_ban_phan_cong(dot_obj, nguoi_dung)
    return xuat_excel_du_thao_phan_cong(bpc)


def xac_nhan_giang_vien_view(request, gv_id, dot_id=None):
    """Giao diện dành cho Giảng viên xác nhận hoặc từ chối sinh viên được phân công (UC10)"""
    try:
        context_data = lay_danh_sach_xac_nhan_cho_giang_vien(gv_id, dot_id)
        context_data["active_sprint"] = 2
        context_data["current_dot"] = context_data.get("dot")
    except Exception as e:
        messages.error(request, str(e))
        return redirect("phancong:dashboard")

    return render(request, "sprint2/lecturer_confirm.html", context_data)


@require_POST
def gv_dong_y_tat_ca_action(request, gv_id, dot_id):
    """Giảng viên bấm nút Đồng ý tất cả sinh viên được phân công"""
    gv = get_object_or_404(giang_vien, id=gv_id)
    dot_obj = get_object_or_404(dot, id=dot_id)
    bpc = get_object_or_404(ban_phan_cong, dot=dot_obj)
    nguoi_dung = _lay_nguoi_thuc_hien(request, dot_obj)

    try:
        ip = request.META.get("REMOTE_ADDR")
        count = gv_dong_y_tat_ca(bpc, gv, nguoi_dung, ip)
        messages.success(request, f"Đã xác nhận đồng ý tiếp nhận toàn bộ {count} sinh viên!")
    except Exception as e:
        messages.error(request, f"Lỗi xác nhận: {str(e)}")

    return redirect("phancong:xac_nhan_giang_vien_dot", gv_id=gv_id, dot_id=dot_id)


@require_POST
def gv_phan_hoi_don_le_action(request, gv_id, pc_id):
    """Giảng viên đồng ý hoặc từ chối từng sinh viên"""
    pc = get_object_or_404(phan_cong_huong_dan, id=pc_id, giang_vien_id=gv_id)
    dot_id = pc.ban_phan_cong.dot_id
    nguoi_dung = _lay_nguoi_thuc_hien(request, pc.ban_phan_cong.dot)

    hanh_dong = request.POST.get("hanh_dong")  # 'DONG_Y' hoặc 'TU_CHOI'
    ly_do = request.POST.get("ly_do", "").strip()

    try:
        ip = request.META.get("REMOTE_ADDR")
        if hanh_dong == "DONG_Y":
            gv_phan_hoi_phan_cong(pc, dong_y=True, ly_do="", nguoi_thuc_hien=nguoi_dung, ip_address=ip)
            messages.success(request, f"Đã đồng ý tiếp nhận sinh viên {pc.ho_so.sinh_vien.nguoi_dung.ho_ten}!")
        elif hanh_dong == "TU_CHOI":
            if not ly_do:
                messages.error(request, "Bắt buộc phải nhập lý do khi từ chối tiếp nhận sinh viên!")
                return redirect("phancong:xac_nhan_giang_vien_dot", gv_id=gv_id, dot_id=dot_id)
            gv_phan_hoi_phan_cong(pc, dong_y=False, ly_do=ly_do, nguoi_thuc_hien=nguoi_dung, ip_address=ip)
            messages.warning(request, f"Đã từ chối tiếp nhận sinh viên {pc.ho_so.sinh_vien.nguoi_dung.ho_ten}. Hồ sơ đã hoàn trả về Trưởng khoa.")
    except Exception as e:
        messages.error(request, f"Lỗi phản hồi: {str(e)}")

    return redirect("phancong:xac_nhan_giang_vien_dot", gv_id=gv_id, dot_id=dot_id)
