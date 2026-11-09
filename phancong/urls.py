from django.urls import path
from . import views

app_name = "phancong"

urlpatterns = [
    # Dashboard Trưởng khoa
    path("", views.sprint2_dashboard_view, name="dashboard"),
    path("<int:dot_id>/", views.sprint2_dashboard_view, name="dashboard_dot"),

    # Hành động phân bổ của Trưởng khoa
    path("<int:dot_id>/snake-draft/", views.chay_snake_draft_action, name="chay_snake_draft"),
    path("<int:dot_id>/gan-thu-cong/", views.gan_thu_cong_action, name="gan_thu_cong"),
    path("<int:dot_id>/xoa-phan-cong/<int:ho_so_id>/", views.xoa_phan_cong_action, name="xoa_phan_cong"),
    path("<int:dot_id>/gui-ban-phan-cong/", views.gui_ban_phan_cong_action, name="gui_ban_phan_cong"),
    path("<int:dot_id>/cong-bo-chinh-thuc/", views.cong_bo_chinh_thuc_action, name="cong_bo_chinh_thuc"),
    path("<int:dot_id>/xuat-excel/", views.xuat_excel_du_thao_action, name="xuat_excel"),

    # Màn hình Giảng viên xác nhận (UC10)
    path("xac-nhan/<int:gv_id>/", views.xac_nhan_giang_vien_view, name="xac_nhan_giang_vien"),
    path("xac-nhan/<int:gv_id>/<int:dot_id>/", views.xac_nhan_giang_vien_view, name="xac_nhan_giang_vien_dot"),
    path("xac-nhan/<int:gv_id>/<int:dot_id>/dong-y-tat-ca/", views.gv_dong_y_tat_ca_action, name="gv_dong_y_tat_ca"),
    path("xac-nhan/<int:gv_id>/phan-hoi/<int:pc_id>/", views.gv_phan_hoi_don_le_action, name="gv_phan_hoi_don_le"),
]
