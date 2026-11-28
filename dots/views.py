"""
Tầng Views cho app dots (Quản lý Đợt).
Tuân thủ mô hình View mỏng: nhận request, gọi selector/service, xử lý thông báo và redirect.
"""
from datetime import datetime
from django.shortcuts import redirect
from django.http import Http404
from django.contrib import messages
from django.utils import timezone
from dots.selectors import get_dot_by_id
from dots.services import cap_nhat_cau_hinh_dot_preset, cap_nhat_trong_so_dot, TrongSoValidationError
from core.constants import ThanhPhanDiem
from accounts.models import nguoi_dung


def switch_dot_view(request, dot_id):
    """
    Chuyển đổi đợt làm việc trong session của người dùng (UC01, UC03).
    Ghi nhớ đợt được chọn và tự động tải lại đúng trang hiện tại.
    """
    dot_obj = get_dot_by_id(dot_id)
    if not dot_obj:
        raise Http404("Không tìm thấy đợt được yêu cầu.")

    request.session['active_dot_id'] = dot_obj.id

    trang_thai_str = dot_obj.get_trang_thai_display()
    messages.success(
        request,
        f"Đã chuyển sang làm việc với: {dot_obj.ten_dot} ({dot_obj.nam_hoc}) - [{trang_thai_str}]"
    )

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('/')


def update_batch_preset_view(request, dot_id):
    """
    Xử lý lưu cấu hình thời lượng đợt và tự động sinh mốc tiến độ (UC03).
    Hỗ trợ 3 mẫu quy chuẩn (15 tuần, 10 tuần, 8 tuần) và 1 mẫu tùy chỉnh.
    """
    if request.method != 'POST':
        return redirect('sprint1_dashboard_dot', dot_id=dot_id)

    dot_obj = get_dot_by_id(dot_id)
    if not dot_obj:
        raise Http404("Không tìm thấy đợt.")

    preset_option = request.POST.get('preset_option', 'DO_AN_15_TUAN')
    raw_start_date = request.POST.get('start_date', '')
    raw_weeks = request.POST.get('total_weeks', '15')

    try:
        total_weeks = int(raw_weeks)
    except (ValueError, TypeError):
        total_weeks = 15

    if raw_start_date:
        try:
            start_date = timezone.make_aware(datetime.strptime(raw_start_date, '%Y-%m-%d'))
        except Exception:
            start_date = timezone.now()
    else:
        start_date = timezone.now()

    # Lấy tài khoản người thực hiện (Trưởng khoa)
    current_user = nguoi_dung.objects.filter(ma_dinh_danh_cong='CB_TK01').first()

    # Gọi service nghiệp vụ tập trung
    _, ten_preset, so_tuan = cap_nhat_cau_hinh_dot_preset(
        dot_obj=dot_obj,
        preset_key=preset_option,
        ngay_bat_dau=start_date,
        tong_so_tuan=total_weeks,
        nguoi_thuc_hien=current_user,
        ip_address=request.META.get('REMOTE_ADDR')
    )

    messages.success(
        request,
        f"Đã cập nhật cấu hình đợt: {ten_preset} ({so_tuan} tuần). Các mốc tiến độ và tỷ trọng điểm đã được tự động tính toán lại vào CSDL!"
    )

    return redirect(f"/sprint1/?section=milestones")


def update_dot_weights_view(request, dot_id):
    """
    Trưởng khoa lưu cấu hình tùy biến phân phối trọng số điểm cho đợt (UC03).
    Hỗ trợ validate tổng 100%, không âm và ghi nhật ký hệ thống.
    """
    if request.method != 'POST':
        return redirect(f"/sprint1/?section=milestones")

    dot_obj = get_dot_by_id(dot_id)
    if not dot_obj:
        raise Http404("Không tìm thấy đợt.")

    current_user = nguoi_dung.objects.filter(ma_dinh_danh_cong='CB_TK01').first()

    raw_weights = {}
    for tp in [ThanhPhanDiem.HUONG_DAN, ThanhPhanDiem.NOI_THUC_TAP, ThanhPhanDiem.PHAN_BIEN, ThanhPhanDiem.HOI_DONG]:
        val_str = request.POST.get(f'weight_{tp}', '0').strip()
        try:
            val = float(val_str) if val_str else 0.0
        except ValueError:
            val = 0.0
        raw_weights[tp] = val

    try:
        cap_nhat_trong_so_dot(
            dot_obj=dot_obj,
            trong_so_dict=raw_weights,
            nguoi_thuc_hien=current_user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(
            request,
            f"Đã lưu thành công cấu hình phân phối điểm cho đợt {dot_obj.ten_dot}! Tỷ lệ đã được cập nhật chính thức vào CSDL."
        )
    except TrongSoValidationError as e:
        messages.error(request, f"Không thể lưu phân bổ điểm: {str(e)}")
    except Exception as e:
        messages.error(request, f"Lỗi hệ thống khi cập nhật trọng số điểm: {str(e)}")

    return redirect(f"/sprint1/?section=milestones")

