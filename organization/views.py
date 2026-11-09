"""
Views cho Cổng Giảng viên (Lecturer Workspace) và Cổng Sinh viên (Student Portal).
Được thiết kế chuyên biệt, tối giản và phân bậc rõ ràng theo vai trò của từng Actor.
"""
from django.shortcuts import render
from dots.models import dot


# Ngân hàng đề tài gợi ý của TS. Cao Thanh Sơn (UC12)
DE_TAI_GOI_Y = [
    {"ma": "DT-KTPM-01", "ten": "Nền tảng thi trắc nghiệm trực tuyến chống gian lận ứng dụng AI", "so_sv": 2, "da_nhan": 2, "con_lai": 0},
    {"ma": "DT-KTPM-02", "ten": "Xây dựng cổng thanh toán học phí tích hợp VietQR động", "so_sv": 1, "da_nhan": 0, "con_lai": 1},
]


def giangvien_portal_view(request):
    """
    CỔNG TÁC NGHIỆP GIẢNG VIÊN - TS. Cao Thanh Sơn (UC10, UC12, UC15, UC18, UC20, UC22, UC24).
    Phân tách rõ ràng 3 vai trò: Hướng dẫn (GVHD), Phản biện (GVPB), và Hội đồng bảo vệ (HĐ).
    """
    current_dot = dot.objects.first()
    sub_tab = request.GET.get("tab", "huongdan")  # 'huongdan' | 'phanbien' | 'hoidong'
    sub_view = request.GET.get("sub", "sinhvien")  # 'sinhvien' | 'detai' | 'tiendo' | 'chamdiem'

    # 1. Danh sách sinh viên hướng dẫn (GVHD)
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

    # 2. Danh sách hồ sơ phân công phản biện (GVPB) - Bảo đảm không trùng SV mình hướng dẫn
    danh_sach_phan_bien = [
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

    # 3. Danh sách Hội đồng bảo vệ (HĐ)
    hoi_dong_info = {
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

    context = {
        "active_sprint": 10,  # Mark as lecturer portal
        "current_dot": current_dot,
        "active_tab": sub_tab,
        "active_sub": sub_view,
        "danh_sach_huong_dan": danh_sach_huong_dan,
        "danh_sach_phan_bien": danh_sach_phan_bien,
        "hoi_dong_info": hoi_dong_info,
        "de_tai_goi_y": DE_TAI_GOI_Y,
    }
    return render(request, "portals/lecturer_portal.html", context)


def sinhvien_portal_view(request):
    """
    CỔNG HỌC TẬP & TỐT NGHIỆP SINH VIÊN - Nguyễn Trọng Mạnh (MSSV: 211108234) (UC11, UC13, UC14, UC16, UC17, UC27).
    Quy trình 4 bước tinh gọn dành riêng cho sinh viên thực hiện đồ án.
    """
    current_dot = dot.objects.first()
    active_step = request.GET.get("step", "1")
    active_sub = request.GET.get("sub", "")

    # Thông tin cá nhân & GVHD
    thong_tin_sv = {
        "ho_ten": "Nguyễn Trọng Mạnh",
        "ma_sv": "211108234",
        "lop": "62K1-CNTT",
        "khoa": "Công nghệ Thông tin & TT",
        "gvhd_ho_ten": "TS. Cao Thanh Sơn",
        "gvhd_ma_cb": "CB_GV01",
        "gvhd_bo_mon": "Bộ môn Kỹ thuật phần mềm",
        "gvhd_email": "sonct@vinhuni.edu.vn",
        "gvhd_sdt": "0988.123.456",
        "trang_thai_ho_so": "DANG_THUC_HIEN",
        "trang_thai_text": "Đang thực hiện đồ án",
    }

    # Đề tài hiện tại của sinh viên
    de_tai_cua_toi = {
        "ten_de_tai": "Nghiên cứu mô hình ngôn ngữ lớn (LLM) và ứng dụng trợ lý học tập cho sinh viên Đại học Vinh",
        "nguon": "SV_DE_XUAT",
        "nguon_text": "Sinh viên tự đề xuất",
        "trang_thai": "CHO_GVHD_DUYET",
        "trang_thai_text": "Chờ TS. Cao Thanh Sơn duyệt",
        "ngay_nop": "06/03/2026",
        "muc_tieu": "Xây dựng pipeline RAG kết hợp LLM nguồn mở để tra cứu giáo trình và quy chế đào tạo tín chỉ.",
        "cong_nghe": "Python, LangChain, FAISS, PyTorch, FastAPI",
    }

    # Nơi thực tập doanh nghiệp
    doanh_nghiep = {
        "ten_cong_ty": "Công ty Cổ phần Phần mềm FPT (FPT Software Đà Nẵng)",
        "dia_chi": "Tòa nhà FPT Complex, Ngũ Hành Sơn, Đà Nẵng",
        "nguoi_huong_dan": "Nguyễn Văn Hùng (Tech Lead)",
        "vi_tri": "Backend AI Engineer (Intern)",
        "trang_thai": "DA_XAC_MINH",
        "trang_thai_text": "Đã xác minh doanh nghiệp",
    }

    # Danh sách các mốc nộp minh chứng tuần
    minh_chung_tuan = [
        {"tuan": "Tuần 3", "tieu_de": "Đề cương chi tiết & Thiết kế CSDL ERD", "ngay_nop": "20/02/2026", "trang_thai": "DAT", "trang_thai_text": "Đã nghiệm thu (Đạt)", "loi_phe": "Đề cương chuẩn, lược đồ CSDL tốt."},
        {"tuan": "Tuần 6", "tieu_de": "Báo cáo tiến độ: Module Authentication & API", "ngay_nop": "10/03/2026", "trang_thai": "DAT", "trang_thai_text": "Đã nghiệm thu (Đạt)", "loi_phe": "Luồng JWT và RBAC hoạt động ổn định."},
        {"tuan": "Tuần 9", "tieu_de": "Báo cáo tiến độ: Tích hợp RAG Pipeline", "ngay_nop": "Chờ nộp (Hạn: 28/03/2026)", "trang_thai": "CHO_NOP", "trang_thai_text": "Đến hạn nộp", "loi_phe": "--"},
    ]

    # Kết quả bảo vệ & điểm số
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
        "active_sprint": 20,  # Mark as student portal
        "current_dot": current_dot,
        "active_step": active_step,
        "active_sub": active_sub,
        "thong_tin_sv": thong_tin_sv,
        "de_tai_cua_toi": de_tai_cua_toi,
        "de_tai_goi_y": DE_TAI_GOI_Y,
        "doanh_nghiep": doanh_nghiep,
        "minh_chung_tuan": minh_chung_tuan,
        "ket_qua": ket_qua,
    }
    return render(request, "portals/student_portal.html", context)
