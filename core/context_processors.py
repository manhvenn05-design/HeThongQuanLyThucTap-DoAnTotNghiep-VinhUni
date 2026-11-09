"""
Context processor cung cấp thông tin Persona và Vai trò (Trưởng khoa, Giảng viên, Sinh viên)
dựa trên tài khoản đăng nhập thực tế của người dùng.
"""
from accounts.models import nguoi_dung
from core.constants import MaVaiTro, LoaiNguoiDung


def persona_context(request):
    user = getattr(request, 'user', None)

    # 1. Xác định qua tài khoản đã đăng nhập
    if user and user.is_authenticated:
        # Trưởng khoa
        if user.is_superuser or user.username in ['truongkhoa', 'CB_TK01']:
            return {
                "current_role": "dean",
                "persona_name": "TS. Phan Anh Phong",
                "persona_role_display": "Trưởng khoa CNTT & TT",
                "persona_code": "CB_TK01",
                "persona_badge": "Trưởng khoa",
                "persona_avatar": "PP",
                "is_authenticated_user": True,
            }
        
        # Giảng viên
        if user.username in ['gv_son', 'CB_GV01'] or user.username.startswith('gv_'):
            return {
                "current_role": "lecturer",
                "persona_name": "TS. Cao Thanh Sơn",
                "persona_role_display": "Giảng viên Bộ môn KTPM",
                "persona_code": "CB_GV01",
                "persona_badge": "Giảng viên",
                "persona_avatar": "CS",
                "is_authenticated_user": True,
            }

        # Sinh viên
        if user.username in ['sv_manh', '211108234'] or user.username.startswith('sv_') or user.username.isdigit():
            return {
                "current_role": "student",
                "persona_name": "Nguyễn Trọng Mạnh",
                "persona_role_display": "Sinh viên Lớp 62K1-CNTT",
                "persona_code": "211108234",
                "persona_badge": "Sinh viên",
                "persona_avatar": "TM",
                "is_authenticated_user": True,
            }

        # Kiểm tra bảng nguoi_dung
        nd = nguoi_dung.objects.filter(ma_dinh_danh_cong__iexact=user.username).first()
        if nd:
            roles = list(nd.phan_quyen_vai_tro.values_list('vai_tro__ma_vai_tro', flat=True))
            if MaVaiTro.TRUONG_KHOA in roles:
                return {
                    "current_role": "dean",
                    "persona_name": nd.ho_ten,
                    "persona_role_display": "Trưởng khoa",
                    "persona_code": nd.ma_dinh_danh_cong,
                    "persona_badge": "Trưởng khoa",
                    "persona_avatar": nd.ho_ten.split()[-1][:2].upper(),
                    "is_authenticated_user": True,
                }
            elif MaVaiTro.GIANG_VIEN in roles or nd.loai_nguoi_dung == LoaiNguoiDung.GIANG_VIEN:
                return {
                    "current_role": "lecturer",
                    "persona_name": nd.ho_ten,
                    "persona_role_display": "Giảng viên",
                    "persona_code": nd.ma_dinh_danh_cong,
                    "persona_badge": "Giảng viên",
                    "persona_avatar": nd.ho_ten.split()[-1][:2].upper(),
                    "is_authenticated_user": True,
                }
            elif nd.loai_nguoi_dung == LoaiNguoiDung.SINH_VIEN:
                return {
                    "current_role": "student",
                    "persona_name": nd.ho_ten,
                    "persona_role_display": "Sinh viên",
                    "persona_code": nd.ma_dinh_danh_cong,
                    "persona_badge": "Sinh viên",
                    "persona_avatar": nd.ho_ten.split()[-1][:2].upper(),
                    "is_authenticated_user": True,
                }

    # 2. Chế độ xem trước (nếu chưa đăng nhập, xác định theo URL hoặc session)
    path = request.path
    if path.startswith("/giangvien/"):
        return {
            "current_role": "lecturer",
            "persona_name": "TS. Cao Thanh Sơn",
            "persona_role_display": "Giảng viên Bộ môn KTPM",
            "persona_code": "CB_GV01",
            "persona_badge": "Giảng viên",
            "persona_avatar": "CS",
            "is_authenticated_user": False,
        }
    elif path.startswith("/sinhvien/"):
        return {
            "current_role": "student",
            "persona_name": "Nguyễn Trọng Mạnh",
            "persona_role_display": "Sinh viên Lớp 62K1-CNTT",
            "persona_code": "211108234",
            "persona_badge": "Sinh viên",
            "persona_avatar": "TM",
            "is_authenticated_user": False,
        }

    # Mặc định Trưởng khoa
    return {
        "current_role": "dean",
        "persona_name": "TS. Phan Anh Phong",
        "persona_role_display": "Trưởng khoa CNTT & TT",
        "persona_code": "CB_TK01",
        "persona_badge": "Trưởng khoa",
        "persona_avatar": "PP",
        "is_authenticated_user": False,
    }


def dot_context(request):
    """
    Context processor cung cấp Ngữ cảnh Đợt toàn cục (Global Academic Batch Context).
    Hỗ trợ chuyển đổi đợt qua session và tự động nhận diện chế độ lưu trữ chỉ đọc.
    """
    from dots.models import dot
    from core.constants import DotTrangThai

    active_dot_id = request.session.get('active_dot_id') if hasattr(request, 'session') else None
    current_dot = None

    if active_dot_id:
        current_dot = dot.objects.filter(id=active_dot_id).first()

    if not current_dot:
        # Ưu tiên lấy đợt đang diễn ra (chưa HOAN_TAT)
        current_dot = dot.objects.exclude(trang_thai=DotTrangThai.HOAN_TAT).first()
        if not current_dot:
            current_dot = dot.objects.first()

    # Lấy toàn bộ danh sách đợt và nhóm theo Năm học -> Học kỳ
    cac_dot = list(dot.objects.select_related('khoa').order_by('-nam_hoc', '-hoc_ky', '-id'))

    # Nhóm theo năm học: dict { nam_hoc: [dot_objects] }
    nhom_nam_hoc = {}
    for d in cac_dot:
        if d.nam_hoc not in nhom_nam_hoc:
            nhom_nam_hoc[d.nam_hoc] = []
        nhom_nam_hoc[d.nam_hoc].append(d)

    is_archived = (current_dot.trang_thai == DotTrangThai.HOAN_TAT) if current_dot else False

    return {
        "current_dot": current_dot,
        "all_dots": cac_dot,
        "nhom_nam_hoc": nhom_nam_hoc,
        "is_archived_batch": is_archived,
    }

