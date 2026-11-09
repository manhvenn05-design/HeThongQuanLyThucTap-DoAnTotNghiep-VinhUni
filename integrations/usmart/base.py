from typing import Protocol, List, Dict, Optional, Any

class UsmartClientProtocol(Protocol):
    """Giao diện chuẩn cho Adapter kết nối cổng USMART Đại học Vinh"""

    def xac_thuc(self, ma_dinh_danh: str, mat_khau: str) -> Optional[Dict[str, Any]]:
        """Xác thực người dùng từ cổng USMART"""
        ...

    def lay_diem_tich_luy_hang_loat(self, danh_sach_mssv: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Lấy điểm trung bình tích lũy hệ 4 và tín chỉ tích lũy cho danh sách sinh viên.
        Trả về dict: { "MSSV": { "diem_tb_he4": 3.25, "tin_chi_tich_luy": 115 } hoặc None }
        """
        ...
