"""
Views cho Sprint 6: Hoàn tất, Khóa sổ điểm & Lưu trữ (UC25 - UC27) và Quản trị hệ thống (UC02, UC29, UC30).
"""
from django.shortcuts import render
from dots.models import dot


def sprint6_dashboard_view(request, dot_id=None):
    """Màn hình chính Sprint 6: Tổng hợp ma trận điểm, Khóa sổ & Xuất bảng điểm tốt nghiệp (UC25 - UC27)"""
    current_dot = dot.objects.filter(id=dot_id).first() if dot_id else dot.objects.first()
    active_tab = request.GET.get("tab", "summary")

    # Bảng tổng hợp kết quả toàn khóa (UC25)
    danh_sach_ket_qua = [
        {
            "stt": 1,
            "ma_sv": "211108234",
            "ten_sv": "Nguyễn Hoàng Long",
            "lop": "62K1-CNTT",
            "ten_de_tai": "Nghiên cứu mô hình ngôn ngữ lớn (LLM) và ứng dụng trợ lý học tập",
            "gvhd": "TS. Nguyễn Văn An",
            "diem_hd": 9.0,
            "diem_pb": 8.5,
            "diem_hdong": 9.2,
            "diem_he10": 8.98,
            "diem_he4": 3.75,
            "diem_chu": "A",
            "xep_loai": "Giỏi",
            "trang_thai": "DA_KHOA_SO",
            "trang_thai_text": "Đã khóa sổ",
        },
        {
            "stt": 2,
            "ma_sv": "211108119",
            "ten_sv": "Phạm Thảo Vy",
            "lop": "62K2-KTPM",
            "ten_de_tai": "Hệ sinh thái Microservices quản lý logistics dựa trên Event-Driven",
            "gvhd": "ThS. Trần Thị Bình",
            "diem_hd": 8.8,
            "diem_pb": 8.2,
            "diem_hdong": 8.6,
            "diem_he10": 8.60,
            "diem_he4": 3.50,
            "diem_chu": "A",
            "xep_loai": "Giỏi",
            "trang_thai": "DA_KHOA_SO",
            "trang_thai_text": "Đã khóa sổ",
        },
        {
            "stt": 3,
            "ma_sv": "211108450",
            "ten_sv": "Trần Quốc Anh",
            "lop": "62K1-CNTT",
            "ten_de_tai": "Hệ thống IoT cảnh báo ngập úng đô thị dựa trên LoRaWAN",
            "gvhd": "ThS. Lê Quốc Cường",
            "diem_hd": 8.5,
            "diem_pb": 8.0,
            "diem_hdong": 8.4,
            "diem_he10": 8.36,
            "diem_he4": 3.20,
            "diem_chu": "B+",
            "xep_loai": "Khá",
            "trang_thai": "DA_KHOA_SO",
            "trang_thai_text": "Đã khóa sổ",
        },
        {
            "stt": 4,
            "ma_sv": "211108032",
            "ten_sv": "Lê Thị Hương",
            "lop": "62K3-HTTT",
            "ten_de_tai": "Ứng dụng xử lý ảnh và YOLOv8 trong giám sát an toàn lao động",
            "gvhd": "TS. Phạm Minh Đức",
            "diem_hd": 9.2,
            "diem_pb": 8.8,
            "diem_hdong": 9.0,
            "diem_he10": 9.04,
            "diem_he4": 3.85,
            "diem_chu": "A",
            "xep_loai": "Xuất sắc",
            "trang_thai": "DA_KHOA_SO",
            "trang_thai_text": "Đã khóa sổ",
        },
        {
            "stt": 5,
            "ma_sv": "211108620",
            "ten_sv": "Vũ Hoài An",
            "lop": "62K2-KTPM",
            "ten_de_tai": "Hệ thống số hóa văn bản scan OCR nhận dạng chữ tiếng Việt viết tay",
            "gvhd": "ThS. Hoàng Thị Dung",
            "diem_hd": 8.5,
            "diem_pb": 8.2,
            "diem_hdong": 8.4,
            "diem_he10": 8.40,
            "diem_he4": 3.30,
            "diem_chu": "B+",
            "xep_loai": "Khá",
            "trang_thai": "DA_KHOA_SO",
            "trang_thai_text": "Đã khóa sổ",
        },
    ]

    context = {
        "active_sprint": 6,
        "active_tab": active_tab,
        "current_dot": current_dot,
        "danh_sach_ket_qua": danh_sach_ket_qua,
        "kpi": {
            "tong_sv": 20,
            "du_dieu_kien": 20,
            "gioi_xuat_sac": 14,
            "ty_le_hoan_thanh": 100,
        }
    }
    return render(request, "sprint6/dashboard.html", context)


def quantri_view(request):
    """Màn hình Cấu hình Danh mục Khoa, Bộ môn & Nhật ký kiểm toán (UC02, UC29, UC30)"""
    context = {
        "active_sprint": 7,
        "tong_so_gv": 28,
        "tong_so_bo_mon": 3,
    }
    return render(request, "quantri/dashboard.html", context)
