"""
Tầng Selectors cho app dots (Quản lý Đợt thực tập / Đồ án tốt nghiệp - UC03).
Chứa toàn bộ các hàm truy vấn dữ liệu đợt và mốc thời gian, trọng số điểm.
"""
from typing import Optional
from django.db.models import QuerySet
from dots.models import dot, dot_moc_thoi_gian, dot_trong_so


def get_all_dots() -> QuerySet:
    """Lấy danh sách tất cả các đợt, sắp xếp mới nhất lên đầu."""
    return dot.objects.select_related('khoa', 'nguoi_tao').order_by('-ngay_tao')


def get_dot_by_id(dot_id: int) -> Optional[dot]:
    """Lấy thông tin một đợt cụ thể theo ID."""
    return dot.objects.select_related('khoa', 'nguoi_tao').filter(id=dot_id).first()


def get_active_dot(session_dot_id: Optional[int] = None) -> Optional[dot]:
    """
    Xác định đợt làm việc hiện tại:
    1. Ưu tiên đợt được lưu trong session (nếu hợp lệ).
    2. Nếu không có, lấy đợt đầu tiên đang ở giai đoạn gần nhất.
    """
    if session_dot_id:
        active = dot.objects.filter(id=session_dot_id).first()
        if active:
            return active
    return dot.objects.order_by('-ngay_tao').first()


def get_dot_milestones(dot_obj: dot) -> QuerySet:
    """Lấy danh sách các mốc thời gian của đợt theo thứ tự tuần tự."""
    return dot_moc_thoi_gian.objects.filter(dot=dot_obj).order_by('thu_tu', 'han_cuoi')


def get_dot_weights(dot_obj: dot) -> QuerySet:
    """Lấy cấu hình trọng số điểm của đợt."""
    return dot_trong_so.objects.filter(dot=dot_obj).order_by('thanh_phan')
