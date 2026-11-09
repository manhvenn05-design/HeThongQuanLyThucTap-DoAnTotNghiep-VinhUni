"""
Dịch vụ xuất danh sách dự thảo phân công hướng dẫn ra file Excel (.xlsx) (UC08).
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from django.http import HttpResponse
from core.constants import PhanCongHuongDanTrangThai


def xuat_excel_du_thao_phan_cong(ban_phan_cong_obj) -> HttpResponse:
    """Tạo file Excel bảng phân công hướng dẫn và trả về HTTP Response"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Phan_Cong_GVHD"

    dot_obj = ban_phan_cong_obj.dot
    khoa_ten = dot_obj.khoa.ten_khoa if dot_obj.khoa else "KHOA CNTT"

    # Style
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Nunito Sans", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Nunito Sans", size=14, bold=True, color="0F172A")
    subtitle_font = Font(name="Nunito Sans", size=11, italic=True, color="475569")
    data_font = Font(name="Nunito Sans", size=10)
    center_align = Alignment(horizontal="center", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")
    border_thin = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # 1. Header văn bản
    ws.merge_cells("A1:G1")
    ws["A1"] = f"TRƯỜNG ĐẠI HỌC VINH - {khoa_ten.upper()}"
    ws["A1"].font = Font(name="Nunito Sans", size=11, bold=True, color="1E3A8A")

    ws.merge_cells("A2:G2")
    ws["A2"] = f"BẢNG PHÂN CÔNG GIẢNG VIÊN HƯỚNG DẪN (DỰ THẢO) - {dot_obj.ten_dot.upper()}"
    ws["A2"].font = title_font

    ws.merge_cells("A3:G3")
    ws["A3"] = f"Mã đợt: {dot_obj.ma_dot} | Trạng thái: {ban_phan_cong_obj.get_trang_thai_display()} | Tối đa {dot_obj.so_sv_toi_da_moi_gv} SV/GV"
    ws["A3"].font = subtitle_font

    # 2. Table Headers
    headers = [
        "STT",
        "Mã sinh viên",
        "Họ và tên sinh viên",
        "Lớp",
        "Giảng viên hướng dẫn",
        "Bộ môn",
        "Hình thức phân công",
        "Trạng thái xác nhận"
    ]

    row_num = 5
    for col_num, h_text in enumerate(headers, 1):
        cell = ws.cell(row=row_num, column=col_num)
        cell.value = h_text
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = border_thin
    ws.row_dimensions[row_num].height = 26

    # 3. Data Rows
    cac_dong = ban_phan_cong_obj.cac_dong_phan_cong.select_related(
        "ho_so__sinh_vien__nguoi_dung",
        "giang_vien__nguoi_dung",
        "giang_vien__bo_mon"
    ).order_by("giang_vien__nguoi_dung__ho_ten", "ho_so__sinh_vien__ma_sinh_vien")

    for idx, d in enumerate(cac_dong, 1):
        row_num += 1
        hinh_thuc = "Snake-draft (Gợi ý)" if d.la_goi_y else "Gán thủ công"
        trang_thai_txt = d.get_trang_thai_display()

        data_cells = [
            (idx, center_align),
            (d.ho_so.sinh_vien.ma_sinh_vien, center_align),
            (d.ho_so.sinh_vien.nguoi_dung.ho_ten, left_align),
            (d.ho_so.sinh_vien.lop or "", center_align),
            (d.giang_vien.nguoi_dung.ho_ten, left_align),
            (d.giang_vien.bo_mon.ten_bo_mon if d.giang_vien.bo_mon else "", left_align),
            (hinh_thuc, center_align),
            (trang_thai_txt, center_align),
        ]

        for col_num, (val, align) in enumerate(data_cells, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = val
            cell.font = data_font
            cell.alignment = align
            cell.border = border_thin

        ws.row_dimensions[row_num].height = 20

    # Auto column width
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"Du_thao_phan_cong_{dot_obj.ma_dot}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response
