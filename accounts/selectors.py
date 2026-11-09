"""
Tầng Selectors cho app accounts.
Chứa các hàm truy vấn thông tin người dùng và phân quyền vai trò.
"""
from typing import Optional
from django.contrib.auth.models import User
from accounts.models import nguoi_dung, vai_tro, nguoi_dung_vai_tro
from core.constants import MaVaiTro, LoaiNguoiDung


def get_nguoi_dung_by_identifier(identifier: str) -> Optional[nguoi_dung]:
    """Tìm bản ghi người dùng theo mã định danh cổng hoặc email."""
    nd = nguoi_dung.objects.filter(ma_dinh_danh_cong__iexact=identifier).first()
    if not nd:
        nd = nguoi_dung.objects.filter(email__iexact=identifier).first()
    return nd


def get_django_user_by_identifier(identifier: str) -> Optional[User]:
    """Tìm Django auth User từ username, mã định danh cổng hoặc email."""
    user = User.objects.filter(username__iexact=identifier).first()
    if not user:
        nd = get_nguoi_dung_by_identifier(identifier)
        if nd:
            user = User.objects.filter(username__in=[identifier.lower(), nd.email]).first()
    return user


def get_user_role(user: User) -> str:
    """
    Xác định vai trò nghiệp vụ chính của người dùng ('dean' | 'lecturer' | 'student').
    """
    if user.is_superuser or user.username in ['truongkhoa', 'CB_TK01']:
        return 'dean'

    nd = get_nguoi_dung_by_identifier(user.username)
    if not nd and user.email:
        nd = get_nguoi_dung_by_identifier(user.email)

    if nd:
        roles = list(nd.phan_quyen_vai_tro.values_list('vai_tro__ma_vai_tro', flat=True))
        if MaVaiTro.TRUONG_KHOA in roles:
            return 'dean'
        if MaVaiTro.GIANG_VIEN in roles or nd.loai_nguoi_dung == LoaiNguoiDung.GIANG_VIEN:
            return 'lecturer'
        if nd.loai_nguoi_dung == LoaiNguoiDung.SINH_VIEN:
            return 'student'

    if user.username.startswith('gv_') or user.username.startswith('CB_GV'):
        return 'lecturer'
    if user.username.startswith('sv_') or user.username.isdigit():
        return 'student'

    return 'dean'
