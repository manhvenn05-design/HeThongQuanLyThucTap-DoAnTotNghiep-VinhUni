"""
Views cho Sprint 3: Đăng ký & Chốt đề tài (UC12, UC13, UC14, UC15).
Phân tầng kiến trúc rõ ràng: View mỏng, chỉ nhận request, gọi Selector/Service, trả về Response.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponse, Http404
from core.constants import DotTrangThai, DeTaiGoiYTrangThai, DeTaiNguon, DeTaiTrangThai
from dots.models import dot
from organization.models import giang_vien, sinh_vien
from hoso.models import ho_so
from detai.models import de_tai_goi_y, de_tai
from accounts.selectors import get_nguoi_dung_by_identifier
from organization.selectors import get_current_lecturer, get_current_student
from detai.selectors import (
    lay_dot_chot_de_tai,
    lay_du_lieu_dashboard_sprint3,
    lay_danh_sach_de_tai_goi_y_cua_gv,
    lay_hang_doi_duyet_de_tai_cho_gv,
    lay_de_tai_goi_y_cho_sinh_vien,
)
from detai.services.topic_service import (
    tao_de_tai_goi_y,
    dong_hoac_mo_de_tai_goi_y,
    sinh_vien_chon_de_tai_goi_y,
    sinh_vien_de_xuat_de_tai,
    gvhd_phe_duyet_de_tai,
    gvhd_duyet_hang_loat_de_tai,
    TopicValidationError,
)
from core.state import chuyen_trang_thai_dot, StateTransitionError


def _lay_nguoi_thuc_hien(request, dot_obj):
    """Lấy bản ghi nguoi_dung từ request hoặc fallback người tạo đợt nếu chưa login"""
    if request.user.is_authenticated:
        nd = get_nguoi_dung_by_identifier(request.user.username)
        if not nd and request.user.email:
            nd = get_nguoi_dung_by_identifier(request.user.email)
        if nd:
            return nd
    return dot_obj.nguoi_tao


def sprint3_dashboard_view(request, dot_id=None):
    """Màn hình chính Sprint 3: Bảng điều hành giám sát & định hướng đề tài toàn khoa (Dành cho Trưởng khoa)"""
    dot_obj = lay_dot_chot_de_tai(dot_id)
    if not dot_obj:
        messages.error(request, "Chưa có đợt thực tập / đồ án nào trong hệ thống!")
        return redirect("/dots/")

    bo_mon_id = request.GET.get("bo_mon")
    bo_mon_id = int(bo_mon_id) if bo_mon_id and bo_mon_id.isdigit() else None
    search_query = request.GET.get("q")
    active_tab = request.GET.get("tab", "queue")

    context_data = lay_du_lieu_dashboard_sprint3(
        dot_obj=dot_obj,
        bo_mon_id=bo_mon_id,
        search_query=search_query
    )
    context_data["active_sprint"] = 3
    context_data["active_tab"] = active_tab

    return render(request, "sprint3/dashboard.html", context_data)


@require_POST
def tao_de_tai_goi_y_action(request):
    """Giảng viên hướng dẫn tạo đề tài gợi ý mới (UC12)"""
    dot_id = request.POST.get("dot_id")
    dot_obj = get_object_or_404(dot, id=dot_id)
    gv = get_current_lecturer(request.user)

    if not gv:
        messages.error(request, "Không xác định được danh tính Giảng viên hướng dẫn!")
        return redirect(request.META.get("HTTP_REFERER", "/giangvien/?tab=huongdan&sub=detai"))

    ten_de_tai = request.POST.get("ten_de_tai", "").strip()
    mo_ta = request.POST.get("mo_ta", "").strip()
    so_luong_str = request.POST.get("so_luong_toi_da", "1").strip()
    so_luong_toi_da = int(so_luong_str) if so_luong_str.isdigit() else 1

    try:
        ip = request.META.get("REMOTE_ADDR")
        nguoi_dung = _lay_nguoi_thuc_hien(request, dot_obj)
        tao_de_tai_goi_y(
            dot_obj=dot_obj,
            giang_vien_obj=gv,
            ten_de_tai=ten_de_tai,
            mo_ta=mo_ta,
            so_luong_toi_da=so_luong_toi_da,
            nguoi_thuc_hien=nguoi_dung,
            ip_address=ip
        )
        messages.success(request, f"Đã thêm thành công đề tài gợi ý: '{ten_de_tai}'!")
    except Exception as e:
        messages.error(request, f"Lỗi tạo đề tài: {str(e)}")

    return redirect(request.META.get("HTTP_REFERER", "/giangvien/?tab=huongdan&sub=detai"))


@require_POST
def doi_trang_thai_goi_y_action(request, gy_id):
    """Giảng viên bật/tắt nhận đăng ký cho đề tài gợi ý"""
    gy = get_object_or_404(de_tai_goi_y, id=gy_id)
    nguoi_dung = _lay_nguoi_thuc_hien(request, gy.dot)
    ip = request.META.get("REMOTE_ADDR")

    mo_moi = (gy.trang_thai != DeTaiGoiYTrangThai.MO)
    dong_hoac_mo_de_tai_goi_y(gy, mo_dang_ky=mo_moi, nguoi_thuc_hien=nguoi_dung, ip_address=ip)

    status_text = "Mở nhận đăng ký" if mo_moi else "Đóng nhận đăng ký"
    messages.success(request, f"Đã chuyển trạng thái đề tài thành: {status_text}!")
    return redirect(request.META.get("HTTP_REFERER", "/giangvien/?tab=huongdan&sub=detai"))


@require_POST
def sinh_vien_dang_ky_de_tai_action(request):
    """Sinh viên chọn đề tài từ gợi ý của GV (UC13) hoặc tự đề xuất đề tài mới (UC14)"""
    sv = get_current_student(request.user)
    if not sv:
        messages.error(request, "Không xác định được danh tính sinh viên đăng nhập!")
        return redirect("/sinhvien/?step=2")

    current_dot = lay_dot_chot_de_tai()
    hs = ho_so.objects.filter(sinh_vien=sv, dot=current_dot).first()
    if not hs:
        hs = ho_so.objects.filter(sinh_vien=sv).order_by("-id").first()

    if not hs:
        messages.error(request, "Không tìm thấy hồ sơ thực tập/đồ án của bạn trong đợt này!")
        return redirect("/sinhvien/?step=2")

    loai_dang_ky = request.POST.get("loai_dang_ky")  # 'GOI_Y' hoặc 'DE_XUAT'
    ip = request.META.get("REMOTE_ADDR")
    nguoi_dung = _lay_nguoi_thuc_hien(request, hs.dot)

    try:
        if loai_dang_ky == "GOI_Y":
            gy_id = request.POST.get("de_tai_goi_y_id")
            if not gy_id:
                messages.error(request, "Vui lòng chọn một đề tài trong danh sách gợi ý!")
                return redirect("/sinhvien/?step=2")
            gy = get_object_or_404(de_tai_goi_y, id=int(gy_id))
            sinh_vien_chon_de_tai_goi_y(hs, gy, nguoi_thuc_hien=nguoi_dung, ip_address=ip)
            messages.success(request, f"Bạn đã chọn đề tài gợi ý '{gy.ten_de_tai}' thành công! Hồ sơ đã gửi đến GVHD chờ phê duyệt.")

        elif loai_dang_ky == "DE_XUAT":
            ten_de_tai = request.POST.get("ten_de_tai", "").strip()
            mo_ta = request.POST.get("mo_ta", "").strip()
            sinh_vien_de_xuat_de_tai(hs, ten_de_tai=ten_de_tai, mo_ta=mo_ta, nguoi_thuc_hien=nguoi_dung, ip_address=ip)
            messages.success(request, f"Đã gửi đề xuất đề tài '{ten_de_tai}' thành công đến Thầy/Cô hướng dẫn!")
        else:
            messages.error(request, "Hình thức đăng ký đề tài không hợp lệ!")
    except Exception as e:
        messages.error(request, f"Không thể đăng ký đề tài: {str(e)}")

    return redirect("/sinhvien/?step=2")


@require_POST
def gvhd_phe_duyet_action(request, de_tai_id):
    """GVHD duyệt chốt (chấp nhận) hoặc trả lại đề tài kèm góp ý (UC15)"""
    dt = get_object_or_404(de_tai, id=de_tai_id)
    nguoi_dung = _lay_nguoi_thuc_hien(request, dt.ho_so.dot)
    ip = request.META.get("REMOTE_ADDR")

    hanh_dong = request.POST.get("hanh_dong")  # 'CHAP_NHAN' hoặc 'TRA_LAI'
    gop_y = request.POST.get("gop_y", "").strip()

    try:
        if hanh_dong == "CHAP_NHAN":
            gvhd_phe_duyet_de_tai(dt, chap_nhan=True, gop_y="", nguoi_thuc_hien=nguoi_dung, ip_address=ip)
            messages.success(request, f"Đã chốt chính thức đề tài '{dt.ten_de_tai}' cho sinh viên {dt.ho_so.sinh_vien.nguoi_dung.ho_ten}! Hồ sơ đã chuyển sang giai đoạn Thực hiện.")
        elif hanh_dong == "TRA_LAI":
            if not gop_y:
                messages.error(request, "Bắt buộc phải nhập ý kiến góp ý khi yêu cầu sinh viên chỉnh sửa đề tài!")
                return redirect(request.META.get("HTTP_REFERER", "/giangvien/?tab=huongdan&sub=detai"))
            gvhd_phe_duyet_de_tai(dt, chap_nhan=False, gop_y=gop_y, nguoi_thuc_hien=nguoi_dung, ip_address=ip)
            messages.warning(request, f"Đã trả lại đề tài cho sinh viên {dt.ho_so.sinh_vien.nguoi_dung.ho_ten} kèm nội dung góp ý chỉnh sửa.")
        else:
            messages.error(request, "Hành động phê duyệt không hợp lệ!")
    except Exception as e:
        messages.error(request, f"Lỗi phê duyệt: {str(e)}")

    return redirect(request.META.get("HTTP_REFERER", "/giangvien/?tab=huongdan&sub=detai"))


@require_POST
def gvhd_duyet_tat_ca_action(request, dot_id):
    """GVHD duyệt đồng loạt tất cả các đề tài đang chờ của sinh viên mình phụ trách"""
    dot_obj = get_object_or_404(dot, id=dot_id)
    gv = get_current_lecturer(request.user)
    if not gv:
        messages.error(request, "Không xác định được giảng viên!")
        return redirect("/giangvien/?tab=huongdan&sub=detai")

    nguoi_dung = _lay_nguoi_thuc_hien(request, dot_obj)
    ip = request.META.get("REMOTE_ADDR")

    # Lấy các đề tài CHO_CHOT của GV này
    ids = list(de_tai.objects.filter(
        ho_so__dot=dot_obj,
        ho_so__giang_vien_huong_dan=gv,
        trang_thai=DeTaiTrangThai.CHO_CHOT
    ).values_list("id", flat=True))

    if not ids:
        messages.info(request, "Không có đề tài nào đang chờ duyệt!")
        return redirect("/giangvien/?tab=huongdan&sub=detai")

    count = gvhd_duyet_hang_loat_de_tai(ids, gv, nguoi_thuc_hien=nguoi_dung, ip_address=ip)
    messages.success(request, f"Đã duyệt chốt chính thức thành công toàn bộ {count} đề tài đồ án!")
    return redirect("/giangvien/?tab=huongdan&sub=detai")


@require_POST
def chuyen_sang_thuc_hien_action(request, dot_id):
    """Trưởng khoa chuyển đợt sang Giai đoạn 4: Thực hiện & Minh chứng"""
    dot_obj = get_object_or_404(dot, id=dot_id)
    nguoi_dung = _lay_nguoi_thuc_hien(request, dot_obj)
    ip = request.META.get("REMOTE_ADDR")

    try:
        chuyen_trang_thai_dot(
            dot_obj=dot_obj,
            trang_thai_moi=DotTrangThai.THUC_HIEN,
            nguoi_thuc_hien=nguoi_dung,
            ly_do="Chuyển sang Giai đoạn 4: Thực hiện đồ án và nộp minh chứng",
            ip_address=ip
        )
        messages.success(request, "Đã chuyển đợt thành công sang Giai đoạn 4: Thực hiện & Nộp minh chứng tiến độ!")
        return redirect("/thuchien/")
    except Exception as e:
        messages.error(request, f"Không thể chuyển giai đoạn: {str(e)}")
        return redirect("detai:dashboard_dot", dot_id=dot_id)
