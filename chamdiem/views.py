"""
Views cho Sprint 5: Đánh giá & Chấm điểm đồ án tốt nghiệp (UC19 - UC24).
Phản ánh ma trận điểm có trọng số: Điểm HD (40%) - Điểm PB (20%) - Điểm HĐ (40%).
"""
from django.shortcuts import render
from dots.models import dot


def sprint5_dashboard_view(request, dot_id=None):
    """Màn hình chính Sprint 5: Đánh giá, Chấm điểm & Hội đồng bảo vệ (UC19 - UC24)"""
    current_dot = dot.objects.filter(id=dot_id).first() if dot_id else dot.objects.first()

    # Dữ liệu mẫu ma trận điểm cho sinh viên bảo vệ
    danh_sach_cham_diem = [
        {
            "id": 1,
            "ma_sv": "211108234",
            "ten_sv": "Nguyễn Hoàng Long",
            "lop": "62K1-CNTT",
            "ten_de_tai": "Nghiên cứu mô hình ngôn ngữ lớn (LLM) và ứng dụng trợ lý học tập",
            "gvhd": "TS. Nguyễn Văn An",
            "diem_hd": 9.0,
            "gvpb": "ThS. Lê Quốc Cường",
            "diem_pb": 8.5,
            "diem_hdong": 9.2,
            "diem_tong_he10": 8.98,
            "diem_he4": 3.75,
            "xep_loai": "Giỏi",
            "trang_thai": "HOAN_TAT",
            "trang_thai_text": "Đã có đủ 3 đầu điểm",
        },
        {
            "id": 2,
            "ma_sv": "211108119",
            "ten_sv": "Phạm Thảo Vy",
            "lop": "62K2-KTPM",
            "ten_de_tai": "Hệ sinh thái Microservices quản lý logistics dựa trên Event-Driven",
            "gvhd": "ThS. Trần Thị Bình",
            "diem_hd": 8.8,
            "gvpb": "TS. Phạm Minh Đức",
            "diem_pb": 8.2,
            "diem_hdong": 8.6,
            "diem_tong_he10": 8.60,
            "diem_he4": 3.50,
            "xep_loai": "Giỏi",
            "trang_thai": "HOAN_TAT",
            "trang_thai_text": "Đã có đủ 3 đầu điểm",
        },
        {
            "id": 3,
            "ma_sv": "211108450",
            "ten_sv": "Trần Quốc Anh",
            "lop": "62K1-CNTT",
            "ten_de_tai": "Hệ thống IoT cảnh báo ngập úng đô thị dựa trên LoRaWAN",
            "gvhd": "ThS. Lê Quốc Cường",
            "diem_hd": 8.5,
            "gvpb": "TS. Nguyễn Văn An",
            "diem_pb": 8.0,
            "diem_hdong": 8.4,
            "diem_tong_he10": 8.36,
            "diem_he4": 3.20,
            "xep_loai": "Khá",
            "trang_thai": "HOAN_TAT",
            "trang_thai_text": "Đã có đủ 3 đầu điểm",
        },
        {
            "id": 4,
            "ma_sv": "211108032",
            "ten_sv": "Lê Thị Hương",
            "lop": "62K3-HTTT",
            "ten_de_tai": "Ứng dụng xử lý ảnh và YOLOv8 trong giám sát an toàn lao động",
            "gvhd": "TS. Phạm Minh Đức",
            "diem_hd": 9.2,
            "gvpb": "ThS. Hoàng Thị Dung",
            "diem_pb": 8.8,
            "diem_hdong": None,
            "diem_tong_he10": None,
            "diem_he4": None,
            "xep_loai": "--",
            "trang_thai": "CHO_HOI_DONG",
            "trang_thai_text": "Chờ Hội đồng chấm",
        },
        {
            "id": 5,
            "ma_sv": "211108620",
            "ten_sv": "Vũ Hoài An",
            "lop": "62K2-KTPM",
            "ten_de_tai": "Hệ thống số hóa văn bản scan OCR nhận dạng chữ tiếng Việt viết tay",
            "gvhd": "ThS. Hoàng Thị Dung",
            "diem_hd": 8.0,
            "gvpb": "ThS. Trần Thị Bình",
            "diem_pb": None,
            "diem_hdong": None,
            "diem_tong_he10": None,
            "diem_he4": None,
            "xep_loai": "--",
            "trang_thai": "CHO_PHAN_BIEN",
            "trang_thai_text": "Chờ Phản biện chấm",
        },
    ]

    # Danh sách các Hội đồng bảo vệ (UC24)
    danh_sach_hoi_dong = [
        {
            "id": 1,
            "ten_hoi_dong": "Hội đồng 01: Kỹ thuật phần mềm & AI",
            "chu_tich": "TS. Nguyễn Văn An",
            "thu_ky": "ThS. Trần Thị Bình",
            "uy_vien": "TS. Phạm Minh Đức",
            "dia_diem": "Phòng Hội thảo 2 - Tòa nhà A1",
            "thoi_gian": "18/05/2026 - 08:00",
            "so_sv": 10,
            "da_cham": 8,
        },
        {
            "id": 2,
            "ten_hoi_dong": "Hội đồng 02: Mạng & Hệ thống thông tin",
            "chu_tich": "TS. Phạm Minh Đức",
            "thu_ky": "ThS. Lê Quốc Cường",
            "uy_vien": "ThS. Hoàng Thị Dung",
            "dia_diem": "Phòng Lab 304 - Nhà Công nghệ",
            "thoi_gian": "19/05/2026 - 13:30",
            "so_sv": 10,
            "da_cham": 6,
        },
    ]

    active_tab = request.GET.get("tab", "matrix")

    context = {
        "active_sprint": 5,
        "current_dot": current_dot,
        "active_tab": active_tab,
        "danh_sach_cham_diem": danh_sach_cham_diem,
        "danh_sach_hoi_dong": danh_sach_hoi_dong,
        "kpi": {
            "tong_sv": 20,
            "da_cham_hd": 19,
            "da_cham_pb": 17,
            "da_cham_hdong": 14,
            "diem_tb_chung": 8.52,
        }
    }
    return render(request, "sprint5/dashboard.html", context)
