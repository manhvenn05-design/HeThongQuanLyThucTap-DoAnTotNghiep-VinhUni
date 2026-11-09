"""
Views cho Sprint 4: Theo dõi thực hiện đồ án & Nộp minh chứng (UC16, UC17, UC18, UC31).
Cung cấp đầy đủ giao diện tiến trình 15 tuần, nhật ký nộp minh chứng và nhận xét của GVHD.
"""
from django.shortcuts import render
from dots.models import dot


def sprint4_dashboard_view(request, dot_id=None):
    """Màn hình chính Sprint 4: Theo dõi tiến độ & Nộp minh chứng đồ án (UC16 - UC18, UC31)"""
    current_dot = dot.objects.filter(id=dot_id).first() if dot_id else dot.objects.first()

    # Thông tin đơn vị thực tập mẫu (UC16)
    doanh_nghiep = {
        "ten_cong_ty": "Công ty Cổ phần Phần mềm FPT (FPT Software Đà Nẵng)",
        "dia_chi": "Tòa nhà FPT Complex, Đường Nam Kỳ Khởi Nghĩa, Ngũ Hành Sơn, Đà Nẵng",
        "ma_so_thue": "0101248141",
        "nguoi_huong_dan_dn": "Nguyễn Văn Hùng",
        "chuc_vu_dn": "Tech Lead - Đơn vị DXT",
        "email_dn": "hungnv@fsoft.com.vn",
        "sdt_dn": "0912.345.678",
        "vi_tri_thuc_tap": "Lập trình viên Backend (Golang / Cloud)",
        "trang_thai_xac_minh": "DA_XAC_MINH",
        "trang_thai_text": "Đã xác minh doanh nghiệp",
    }

    # Danh sách các mốc nộp minh chứng (UC17)
    danh_sach_minh_chung = [
        {
            "id": 1,
            "tuan": "Tuần 3",
            "tieu_de": "Báo cáo đề cương chi tiết & Thiết kế cơ sở dữ liệu ERD",
            "ngay_nop": "20/02/2026 16:45",
            "file_dinh_kem": "De_cuong_chi_tiet_K62_LongNH.pdf (2.4 MB)",
            "trang_thai": "DAT",
            "trang_thai_text": "Đã nghiệm thu (Đạt)",
            "nhan_xet_gv": "Đề cương rõ ràng, lược đồ CSDL chuẩn hóa 3NF tốt. Tiếp tục triển khai API.",
            "gv_nhan_xet": "TS. Nguyễn Văn An",
            "ngay_nhan_xet": "22/02/2026",
        },
        {
            "id": 2,
            "tuan": "Tuần 6",
            "tieu_de": "Báo cáo tiến độ Phase 1: Xây dựng Module Authentication & API Gateway",
            "ngay_nop": "10/03/2026 11:20",
            "file_dinh_kem": "Bao_cao_Phase1_Source_Git.zip (15.8 MB)",
            "trang_thai": "DAT",
            "trang_thai_text": "Đã nghiệm thu (Đạt)",
            "nhan_xet_gv": "Đã kiểm tra code trên GitHub, luồng JWT và RBAC hoạt động ổn định.",
            "gv_nhan_xet": "TS. Nguyễn Văn An",
            "ngay_nhan_xet": "12/03/2026",
        },
        {
            "id": 3,
            "tuan": "Tuần 9",
            "tieu_de": "Báo cáo tiến độ Phase 2: Tích hợp RAG Pipeline và kiểm thử hiệu năng",
            "ngay_nop": "25/03/2026 09:30",
            "file_dinh_kem": "Bao_cao_RAG_Test_Latency.pdf (4.1 MB)",
            "trang_thai": "CHO_NHAN_XET",
            "trang_thai_text": "Chờ GVHD nhận xét",
            "nhan_xet_gv": "Đang xem xét nội dung và kết quả benchmark độ trễ.",
            "gv_nhan_xet": "TS. Nguyễn Văn An",
            "ngay_nhan_xet": "--",
        },
        {
            "id": 4,
            "tuan": "Tuần 12",
            "tieu_de": "Dự thảo báo cáo toàn văn tốt nghiệp & Link video demo hệ thống",
            "ngay_nop": "Chưa nộp (Hạn: 15/04/2026)",
            "file_dinh_kem": "--",
            "trang_thai": "CHUA_NOP",
            "trang_thai_text": "Chưa đến hạn",
            "nhan_xet_gv": "--",
            "gv_nhan_xet": "TS. Nguyễn Văn An",
            "ngay_nhan_xet": "--",
        },
    ]

    active_tab = request.GET.get("tab", "timeline")

    context = {
        "active_sprint": 4,
        "current_dot": current_dot,
        "active_tab": active_tab,
        "doanh_nghiep": doanh_nghiep,
        "danh_sach_minh_chung": danh_sach_minh_chung,
        "kpi": {
            "tuan_hien_tai": 8,
            "tong_so_tuan": 15,
            "phan_tram_tuan": 53,
            "so_moc_da_dat": 2,
            "tong_so_moc": 4,
            "moc_ke_tiep": "Mốc 3 (Còn 3 ngày)",
        }
    }
    return render(request, "sprint4/dashboard.html", context)
