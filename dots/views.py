"""
Tầng Views cho app dots (Quản lý Đợt).
Tuân thủ mô hình View mỏng: nhận request, gọi selector/service, xử lý thông báo và redirect.
"""
from django.shortcuts import redirect
from django.http import Http404
from django.contrib import messages
from dots.selectors import get_dot_by_id


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
