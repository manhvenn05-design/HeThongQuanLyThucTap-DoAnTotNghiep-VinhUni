"""
Tầng Views cho app accounts.
Tuân thủ mô hình View mỏng: chỉ tiếp nhận request, gọi Selector/Service và render template.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from accounts.selectors import get_user_role
from accounts.services import xac_thuc_nguoi_dung_da_nang, ghi_nhan_dang_nhap_thanh_cong


def login_view(request):
    """
    Trang đăng nhập tối giản, trang trọng và chuẩn mực học thuật.
    Hỗ trợ đăng nhập đa năng (username, mã cán bộ, MSSV, email).
    Luôn hiển thị màn hình đăng nhập để người dùng chủ động chọn vai trò khi khởi động.
    """
    error_message = None

    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = xac_thuc_nguoi_dung_da_nang(request, identifier, password)

        if user is not None:
            if not user.is_active:
                error_message = "Tài khoản của bạn hiện đang bị tạm khóa."
            else:
                login(request, user)
                ghi_nhan_dang_nhap_thanh_cong(user)

                role = get_user_role(user)
                request.session['current_role'] = role

                # Điều hướng theo vai trò thực tế
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)

                if role == 'lecturer':
                    return redirect('giangvien_portal')
                elif role == 'student':
                    return redirect('sinhvien_portal')
                else:
                    return redirect('sprint1_dashboard')
        else:
            error_message = "Mã tài khoản hoặc mật khẩu không chính xác. Vui lòng kiểm tra lại."

    return render(request, 'accounts/login.html', {
        'error_message': error_message,
    })


def logout_view(request):
    """Đăng xuất khỏi hệ thống và xóa phiên làm việc."""
    logout(request)
    return redirect('login')
