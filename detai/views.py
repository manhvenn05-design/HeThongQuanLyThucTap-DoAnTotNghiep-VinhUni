"""
Views cho Sprint 3: Chọn & Chốt đề tài (UC12, UC13, UC14, UC15).
Cung cấp đầy đủ giao diện và dữ liệu mẫu phong phú để duyệt, điều phối 2 chiều giữa GV và SV.
"""
from django.shortcuts import render
from django.contrib import messages
from dots.models import dot
from organization.models import giang_vien, bo_mon


def sprint3_dashboard_view(request, dot_id=None):
    """Màn hình chính Sprint 3: Quản lý Hàng đợi & Duyệt Đề tài Hai Chiều (UC12 - UC15)"""
    current_dot = dot.objects.filter(id=dot_id).first() if dot_id else dot.objects.first()

    # Dữ liệu mẫu phong phú cho hàng đợi duyệt đề tài (UC15)
    danh_sach_cho_duyet = [
        {
            "id": 1,
            "ma_sv": "211108234",
            "ten_sv": "Nguyễn Hoàng Long",
            "lop": "62K1-CNTT",
            "ten_de_tai": "Nghiên cứu mô hình ngôn ngữ lớn (LLM) và ứng dụng trợ lý học tập cho sinh viên Đại học Vinh",
            "gvhd": "TS. Nguyễn Văn An",
            "bo_mon": "Kỹ thuật phần mềm",
            "nguon": "SV_DE_XUAT",
            "nguon_text": "Sinh viên tự đề xuất",
            "trang_thai": "CHO_GVHD_DUYET",
            "trang_thai_text": "Chờ GVHD phê duyệt",
            "ngay_nop": "06/03/2026 14:30",
            "muc_tieu": "Xây dựng pipeline RAG kết hợp LLM nguồn mở để tra cứu giáo trình và quy chế đào tạo tín chỉ.",
            "cong_nghe": "Python, LangChain, FAISS, PyTorch, FastAPI",
        },
        {
            "id": 2,
            "ma_sv": "211108119",
            "ten_sv": "Phạm Thảo Vy",
            "lop": "62K2-KTPM",
            "ten_de_tai": "Xây dựng hệ sinh thái Microservices quản lý logistics dựa trên kiến trúc Event-Driven và Kubernetes",
            "gvhd": "ThS. Trần Thị Bình",
            "bo_mon": "Kỹ thuật phần mềm",
            "nguon": "SV_DE_XUAT",
            "nguon_text": "Sinh viên tự đề xuất",
            "trang_thai": "CHO_GVHD_DUYET",
            "trang_thai_text": "Chờ GVHD phê duyệt",
            "ngay_nop": "07/03/2026 09:15",
            "muc_tieu": "Thiết kế kiến trúc chịu tải cao với Apache Kafka, gRPC và triển khai hạ tầng tự động CI/CD.",
            "cong_nghe": "Golang, Docker, Kubernetes, Apache Kafka, PostgreSQL",
        },
    ]

    # Danh sách đề tài đã chốt chính thức
    danh_sach_da_chot = [
        {
            "id": 3,
            "ma_sv": "211108450",
            "ten_sv": "Trần Quốc Anh",
            "lop": "62K1-CNTT",
            "ten_de_tai": "Hệ thống IoT cảnh báo ngập úng đô thị dựa trên mạng cảm biến không dây và học sâu dự báo mực nước",
            "gvhd": "ThS. Lê Quốc Cường",
            "bo_mon": "Mạng máy tính & TT",
            "nguon": "GV_GOI_Y",
            "nguon_text": "Ngân hàng đề tài GV",
            "trang_thai": "DA_CHOT",
            "trang_thai_text": "Đã chốt chính thức",
            "ngay_chot": "04/03/2026",
            "muc_tieu": "Thu thập dữ liệu mực nước thời gian thực qua LoRaWAN và cảnh báo qua ứng dụng di động.",
            "cong_nghe": "ESP32, LoRaWAN, Node.js, TensorFlow Lite, Flutter",
        },
        {
            "id": 4,
            "ma_sv": "211108032",
            "ten_sv": "Lê Thị Hương",
            "lop": "62K3-HTTT",
            "ten_de_tai": "Ứng dụng công nghệ xử lý ảnh và YOLOv8 trong giám sát an toàn lao động tại công trường xây dựng",
            "gvhd": "TS. Phạm Minh Đức",
            "bo_mon": "Hệ thống thông tin",
            "nguon": "GV_GOI_Y",
            "nguon_text": "Ngân hàng đề tài GV",
            "trang_thai": "DA_CHOT",
            "trang_thai_text": "Đã chốt chính thức",
            "ngay_chot": "05/03/2026",
            "muc_tieu": "Nhận diện người lao động không đội mũ bảo hộ, cảnh báo thời gian thực với độ trễ dưới 200ms.",
            "cong_nghe": "Python, OpenCV, YOLOv8, TensorRT, Flask",
        },
        {
            "id": 5,
            "ma_sv": "211108620",
            "ten_sv": "Vũ Hoài An",
            "lop": "62K2-KTPM",
            "ten_de_tai": "Hệ thống số hóa văn bản lưu trữ trường đại học áp dụng OCR nhận dạng chữ tiếng Việt viết tay",
            "gvhd": "ThS. Hoàng Thị Dung",
            "bo_mon": "Kỹ thuật phần mềm",
            "nguon": "SV_DE_XUAT",
            "nguon_text": "Sinh viên tự đề xuất",
            "trang_thai": "DA_CHOT",
            "trang_thai_text": "Đã chốt chính thức",
            "ngay_chot": "05/03/2026",
            "muc_tieu": "Trích xuất thông tin tự động từ hồ sơ sinh viên scan với độ chính xác trên 92%.",
            "cong_nghe": "Python, Tesseract OCR, CRNN, ReactJS, MongoDB",
        },
    ]

    # Ngân hàng đề tài gợi ý của giảng viên (UC12)
    ngan_hang_goi_y = [
        {
            "id": 101,
            "ma_de_tai": "DT-KTPM-01",
            "ten_de_tai": "Nền tảng thi trắc nghiệm trực tuyến chống gian lận ứng dụng AI theo dõi chuyển động mắt và gương mặt",
            "gv_de_xuat": "TS. Nguyễn Văn An",
            "bo_mon": "Kỹ thuật phần mềm",
            "so_sv_toi_da": 2,
            "da_dang_ky": 2,
            "con_lai": 0,
            "trang_thai": "DA_HET_CHO",
            "trang_thai_text": "Đã nhận đủ",
            "mo_ta": "Tích hợp MediaPipe theo dõi ánh mắt và phát hiện có người thứ hai qua webcam của thí sinh.",
        },
        {
            "id": 102,
            "ma_de_tai": "DT-MMT-02",
            "ten_de_tai": "Xây dựng hệ thống phát hiện tấn công DDoS trên mạng cục bộ sử dụng mô hình học máy Random Forest",
            "gv_de_xuat": "ThS. Lê Quốc Cường",
            "bo_mon": "Mạng máy tính & TT",
            "so_sv_toi_da": 2,
            "da_dang_ky": 1,
            "con_lai": 1,
            "trang_thai": "CON_CHO",
            "trang_thai_text": "Còn 1 chỗ",
            "mo_ta": "Bắt gói tin mạng với Scapy, trích xuất đặc trưng lưu lượng và huấn luyện bộ phân lớp.",
        },
        {
            "id": 103,
            "ma_de_tai": "DT-HTTT-03",
            "ten_de_tai": "Hệ thống gợi ý học phần và lộ trình chứng chỉ công nghệ thông tin cho sinh viên dựa trên Collaborative Filtering",
            "gv_de_xuat": "TS. Phạm Minh Đức",
            "bo_mon": "Hệ thống thông tin",
            "so_sv_toi_da": 2,
            "da_dang_ky": 0,
            "con_lai": 2,
            "trang_thai": "MO",
            "trang_thai_text": "Đang mở (2 chỗ)",
            "mo_ta": "Phân tích bảng điểm và sở thích hướng nghiệp để đề xuất môn học tự chọn phù hợp nhất.",
        },
        {
            "id": 104,
            "ma_de_tai": "DT-KTPM-04",
            "ten_de_tai": "Xây dựng cổng thanh toán học phí tích hợp VietQR động và đối soát giao dịch ngân hàng tự động",
            "gv_de_xuat": "ThS. Hoàng Thị Dung",
            "bo_mon": "Kỹ thuật phần mềm",
            "so_sv_toi_da": 1,
            "da_dang_ky": 0,
            "con_lai": 1,
            "trang_thai": "MO",
            "trang_thai_text": "Đang mở (1 chỗ)",
            "mo_ta": "Giao tiếp Webhook cổng Napas và đối chiếu dữ liệu giao dịch định kỳ theo chuẩn ngân hàng.",
        },
    ]

    active_tab = request.GET.get("tab", "queue")

    context = {
        "active_sprint": 3,
        "current_dot": current_dot,
        "active_tab": active_tab,
        "danh_sach_cho_duyet": danh_sach_cho_duyet,
        "danh_sach_da_chot": danh_sach_da_chot,
        "ngan_hang_goi_y": ngan_hang_goi_y,
        "kpi": {
            "quota_tong": 20,
            "quota_phan_bo": 20,
            "da_chot": len(danh_sach_da_chot),
            "cho_duyet": len(danh_sach_cho_duyet),
            "goi_y_tong": len(ngan_hang_goi_y),
            "goi_y_con_cho": 2,
            "phan_tram_chot": 60,
        }
    }
    return render(request, "sprint3/dashboard.html", context)
