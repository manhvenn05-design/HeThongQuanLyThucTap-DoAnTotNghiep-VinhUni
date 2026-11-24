"""
Views cho Cổng Giảng viên (Lecturer Workspace) và Cổng Sinh viên (Student Portal).
Được thiết kế chuyên biệt, tối giản và phân bậc rõ ràng theo vai trò của từng Actor.
Tuân thủ nghiêm ngặt mô hình Phân tầng Django MVT: View mỏng, gọi Selectors lấy dữ liệu.
"""
from django.shortcuts import render
from organization.selectors import (
    lay_du_lieu_cong_giang_vien,
    lay_du_lieu_cong_sinh_vien,
)

# Ngân hàng đề tài gợi ý của TS. Cao Thanh Sơn (UC12)
DE_TAI_GOI_Y = [
    {"ma": "DT-KTPM-01", "ten": "Nền tảng thi trắc nghiệm trực tuyến chống gian lận ứng dụng AI", "so_sv": 2, "da_nhan": 2, "con_lai": 0},
    {"ma": "DT-KTPM-02", "ten": "Xây dựng cổng thanh toán học phí tích hợp VietQR động", "so_sv": 1, "da_nhan": 0, "con_lai": 1},
]

# Dữ liệu tĩnh bổ trợ cho các Sprint tương lai (Phản biện UC22, Hội đồng UC24)
DANH_SACH_PHAN_BIEN_MAU = [
    {
        "id": 10,
        "ma_sv": "211108119",
        "ten_sv": "Phạm Thảo Vy",
        "lop": "62K2-KTPM",
        "gvhd": "ThS. Trần Thị Bình",
        "de_tai": "Hệ sinh thái Microservices quản lý logistics dựa trên Event-Driven",
        "file_bao_cao": "Bao_cao_toan_van_ThaoVy_KTPM.pdf (12.4 MB)",
        "link_code": "github.com/vypam/logistics-microservices",
        "diem_pb": 8.5,
        "trang_thai": "DA_CHAM",
    },
    {
        "id": 11,
        "ma_sv": "211108032",
        "ten_sv": "Lê Thị Hương",
        "lop": "62K3-HTTT",
        "gvhd": "TS. Phạm Minh Đức",
        "de_tai": "Ứng dụng xử lý ảnh và YOLOv8 trong giám sát an toàn lao động",
        "file_bao_cao": "Bao_cao_HTTT_LeThiHuong.pdf (8.2 MB)",
        "link_code": "github.com/huongle/yolov8-safety",
        "diem_pb": None,
        "trang_thai": "CHO_CHAM",
    },
]

HOI_DONG_INFO_MAU = {
    "ten_hoi_dong": "Hội đồng 01: Kỹ thuật phần mềm & AI",
    "vai_tro_cua_toi": "Thư ký Hội đồng",
    "chu_tich": "TS. Phan Anh Phong",
    "uy_vien": "TS. Phạm Minh Đức",
    "thoi_gian": "08:00 Ngày 18/05/2026",
    "dia_diem": "Phòng Hội thảo 2 - Tòa nhà A1",
    "so_sv_bao_ve": 10,
    "danh_sach_sv": [
        {"ma_sv": "211108234", "ten_sv": "Nguyễn Trọng Mạnh", "de_tai": "Mô hình LLM và trợ lý học tập", "gio": "08:15", "diem_hdong": None},
        {"ma_sv": "211108119", "ten_sv": "Phạm Thảo Vy", "de_tai": "Kiến trúc Microservices Event-Driven", "gio": "08:45", "diem_hdong": 8.6},
        {"ma_sv": "211108450", "ten_sv": "Trần Quốc Anh", "de_tai": "Hệ thống IoT cảnh báo ngập lụt", "gio": "09:15", "diem_hdong": 8.4},
    ]
}


def giangvien_portal_view(request):
    """
    CỔNG TÁC NGHIỆP GIẢNG VIÊN (UC10, UC12, UC15, UC18, UC20, UC22, UC24).
    Phân tách rõ ràng 3 vai trò: Hướng dẫn (GVHD), Phản biện (GVPB), và Hội đồng bảo vệ (HĐ).
    Tích hợp dữ liệu phân công thực tế từ Sprint 2, bảo đảm Giảng viên không thấy GPA đầu vào (Rule 3).
    """
    dot_id = request.GET.get("dot_id")
    dot_id_int = int(dot_id) if dot_id and dot_id.isdigit() else None
    gv_data = lay_du_lieu_cong_giang_vien(request.user, dot_id=dot_id_int)

    sub_tab = request.GET.get("tab", "huongdan")  # 'huongdan' | 'phanbien' | 'hoidong'
    sub_view = request.GET.get("sub", "sinhvien")  # 'sinhvien' | 'detai' | 'tiendo' | 'chamdiem'

    # Sử dụng danh sách phân công thực tế từ Sprint 2 nếu có
    danh_sach_huong_dan = gv_data["danh_sach_huong_dan"]
    if not danh_sach_huong_dan:
        danh_sach_huong_dan = [
            {
                "id": 1,
                "ma_sv": "211108234",
                "ten_sv": "Nguyễn Trọng Mạnh",
                "lop": "62K1-CNTT",
                "de_tai": "Nghiên cứu mô hình ngôn ngữ lớn (LLM) và ứng dụng trợ lý học tập cho sinh viên",
                "trang_thai_de_tai": "CHO_DUYET",
                "trang_thai_text": "Chờ thầy duyệt đề tài",
                "tien_do": "Tuần 8 / 15",
                "diem_hd": None,
            },
            {
                "id": 2,
                "ma_sv": "211108450",
                "ten_sv": "Trần Quốc Anh",
                "lop": "62K1-CNTT",
                "de_tai": "Hệ thống IoT cảnh báo ngập úng đô thị dựa trên mạng cảm biến không dây",
                "trang_thai_de_tai": "DA_CHOT",
                "trang_thai_text": "Đã chốt chính thức",
                "tien_do": "Tuần 8 / 15",
                "diem_hd": 8.5,
            },
            {
                "id": 3,
                "ma_sv": "211108781",
                "ten_sv": "Đặng Văn Dũng",
                "lop": "62K1-CNTT",
                "de_tai": "Xây dựng ứng dụng Flutter quản trị kho hàng tích hợp mã vạch",
                "trang_thai_de_tai": "DA_CHOT",
                "trang_thai_text": "Đã chốt chính thức",
                "tien_do": "Tuần 8 / 15",
                "diem_hd": None,
            },
            {
                "id": 4,
                "ma_sv": "211108099",
                "ten_sv": "Hoàng Kim Chi",
                "lop": "62K2-KTPM",
                "de_tai": "Nền tảng thương mại điện tử tích hợp thanh toán VietQR động",
                "trang_thai_de_tai": "DA_CHOT",
                "trang_thai_text": "Đã chốt chính thức",
                "tien_do": "Tuần 8 / 15",
                "diem_hd": 9.0,
            },
        ]

    context = {
        **gv_data,
        "active_sprint": 10,  # Đánh dấu đang ở Cổng Giảng viên
        "active_tab": sub_tab,
        "active_sub": sub_view,
        "danh_sach_huong_dan": danh_sach_huong_dan,
        "danh_sach_phan_bien": DANH_SACH_PHAN_BIEN_MAU,
        "hoi_dong_info": HOI_DONG_INFO_MAU,
        "de_tai_goi_y": DE_TAI_GOI_Y,
    }
    return render(request, "portals/lecturer_portal.html", context)


def sinhvien_portal_view(request):
    """
    CỔNG HỌC TẬP & TỐT NGHIỆP SINH VIÊN (UC11, UC13, UC14, UC16, UC17, UC27).
    Quy trình 4 bước tinh gọn dành riêng cho sinh viên thực hiện đồ án.
    Tuân thủ UC11: Thông tin GVHD được cập nhật theo kết quả phân công chính thức.
    """
    dot_id = request.GET.get("dot_id")
    dot_id_int = int(dot_id) if dot_id and dot_id.isdigit() else None
    sv_data = lay_du_lieu_cong_sinh_vien(request.user, dot_id=dot_id_int)

    active_step = request.GET.get("step", "1")
    active_sub = request.GET.get("sub", "")

    # Đề tài hiện tại của sinh viên (Sprint 3)
    de_tai_cua_toi = {
        "ten_de_tai": "Nghiên cứu mô hình ngôn ngữ lớn (LLM) và ứng dụng trợ lý học tập cho sinh viên Đại học Vinh",
        "nguon": "SV_DE_XUAT",
        "nguon_text": "Sinh viên tự đề xuất",
        "trang_thai": "CHO_GVHD_DUYET",
        "trang_thai_text": f"Chờ {sv_data['thong_tin_sv']['gvhd_ho_ten'] or 'GVHD'} duyệt" if sv_data['thong_tin_sv']['da_co_gvhd'] else "Chờ phân công GVHD",
        "ngay_nop": "06/03/2026",
        "muc_tieu": "Xây dựng pipeline RAG kết hợp LLM nguồn mở để tra cứu giáo trình và quy chế đào tạo tín chỉ.",
        "cong_nghe": "Python, LangChain, FAISS, PyTorch, FastAPI",
    }

    # Nơi thực tập doanh nghiệp (Sprint 4)
    doanh_nghiep = {
        "ten_cong_ty": "Công ty Cổ phần Phần mềm FPT (FPT Software Đà Nẵng)",
        "dia_chi": "Tòa nhà FPT Complex, Ngũ Hành Sơn, Đà Nẵng",
        "nguoi_huong_dan": "Nguyễn Văn Hùng (Tech Lead)",
        "vi_tri": "Backend AI Engineer (Intern)",
        "trang_thai": "DA_XAC_MINH",
        "trang_thai_text": "Đã xác minh doanh nghiệp",
    }

    # Danh sách các mốc nộp minh chứng tuần (Sprint 4)
    minh_chung_tuan = [
        {"tuan": "Tuần 3", "tieu_de": "Đề cương chi tiết & Thiết kế CSDL ERD", "ngay_nop": "20/02/2026", "trang_thai": "DAT", "trang_thai_text": "Đã nghiệm thu (Đạt)", "loi_phe": "Đề cương chuẩn, lược đồ CSDL tốt."},
        {"tuan": "Tuần 6", "tieu_de": "Báo cáo tiến độ: Module Authentication & API", "ngay_nop": "10/03/2026", "trang_thai": "DAT", "trang_thai_text": "Đã nghiệm thu (Đạt)", "loi_phe": "Luồng JWT và RBAC hoạt động ổn định."},
        {"tuan": "Tuần 9", "tieu_de": "Báo cáo tiến độ: Tích hợp RAG Pipeline", "ngay_nop": "Chờ nộp (Hạn: 28/03/2026)", "trang_thai": "CHO_NOP", "trang_thai_text": "Đến hạn nộp", "loi_phe": "--"},
    ]

    # Kết quả bảo vệ & điểm số (Sprint 5)
    ket_qua = {
        "lich_bao_ve": "08:15 Ngày 18/05/2026 tại Phòng Hội thảo 2 - Tòa A1",
        "hoi_dong": "Hội đồng 01: Kỹ thuật phần mềm & AI",
        "diem_hd": 9.0,
        "diem_pb": 8.5,
        "diem_hdong": 9.2,
        "diem_tong_he10": 8.98,
        "diem_he4": 3.75,
        "diem_chu": "A",
        "xep_loai": "Giỏi",
        "trang_thai_khoa_so": "Đã khóa sổ & Lưu trữ CSDL",
    }

    context = {
        **sv_data,
        "active_sprint": 20,  # Đánh dấu đang ở Cổng Sinh viên
        "active_step": active_step,
        "active_sub": active_sub,
        "de_tai_cua_toi": de_tai_cua_toi,
        "de_tai_goi_y": DE_TAI_GOI_Y,
        "doanh_nghiep": doanh_nghiep,
        "minh_chung_tuan": minh_chung_tuan,
        "ket_qua": ket_qua,
    }
    return render(request, "portals/student_portal.html", context)
