"""
Tầng Services cho app accounts.
Chứa logic xác thực người dùng đa năng và cập nhật trạng thái phiên đăng nhập.
"""
from typing import Optional, Tuple
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import nguoi_dung
from accounts.selectors import get_django_user_by_identifier, get_nguoi_dung_by_identifier


def xac_thuc_nguoi_dung_da_nang(request, identifier: str, password: str) -> Optional[User]:
    """
    Xác thực đăng nhập đa năng:
    Hỗ trợ username, mã định danh cán bộ (CB_TK01, CB_GV01...), MSSV (211108234), hoặc email.
    """
    # 1. Thử xác thực trực tiếp bằng username
    user = authenticate(request, username=identifier, password=password)
    if user:
        return user

    # 2. Thử ánh xạ qua mã định danh hoặc email
    target_user = get_django_user_by_identifier(identifier)
    if target_user:
        user = authenticate(request, username=target_user.username, password=password)
        if user:
            return user

    return None


def ghi_nhan_dang_nhap_thanh_cong(user: User):
    """Cập nhật thời gian đăng nhập cuối cùng vào bảng nguoi_dung."""
    nd = get_nguoi_dung_by_identifier(user.username)
    if nd:
        nd.lan_dang_nhap_cuoi = timezone.now()
        nd.save(update_fields=['lan_dang_nhap_cuoi'])
