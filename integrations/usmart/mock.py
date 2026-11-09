"""
Bộ giả lập kết nối cổng sinh viên USMART (Mock Adapter)
Phục vụ chạy thử nghiệm phát triển cục bộ theo mục 9 & mục 18 trong PROJECT_SPEC.
"""
import random
import hashlib
from typing import List, Dict, Optional, Any
from .base import UsmartClientProtocol

class MockUsmartClient(UsmartClientProtocol):
    """
    Mock USMART Adapter.
    Sinh điểm trung bình hệ 4 (1.8 - 3.9) và tín chỉ (90 - 135) có tính tất định theo MSSV.
    Mô phỏng trường hợp có khoảng 10% sinh viên chưa có điểm (trả về None).
    """

    def xac_thuc(self, ma_dinh_danh: str, mat_khau: str) -> Optional[Dict[str, Any]]:
        # Giả lập xác thực: Mật khẩu mặc định '123456' hoặc bất kỳ chuỗi nào cho dev
        if not ma_dinh_danh:
            return None
        return {
            "ma_dinh_danh": ma_dinh_danh,
            "ho_ten": f"Người dùng {ma_dinh_danh}",
            "email": f"{ma_dinh_danh.lower()}@vinhuni.edu.vn",
            "thanh_cong": True,
        }

    def lay_diem_tich_luy_hang_loat(self, danh_sach_mssv: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        ket_qua = {}
        for mssv in danh_sach_mssv:
            mssv_clean = str(mssv).strip().upper()
            # Dùng hash của MSSV để sinh điểm tất định (cùng 1 sinh viên thì luôn ra điểm như nhau)
            hash_val = int(hashlib.md5(mssv_clean.encode()).hexdigest(), 16)
            
            # 10% sinh viên không có điểm
            if hash_val % 10 == 0:
                ket_qua[mssv_clean] = None
            else:
                # Điểm hệ 4: từ 2.00 đến 3.85
                diem = round(2.0 + (hash_val % 185) / 100.0, 2)
                # Tín chỉ tích lũy: từ 95 đến 130
                tin_chi = 95 + (hash_val % 36)
                ket_qua[mssv_clean] = {
                    "diem_tb_he4": diem,
                    "tin_chi_tich_luy": tin_chi,
                }
        return ket_qua

# Instance dùng chung
usmart_client = MockUsmartClient()
