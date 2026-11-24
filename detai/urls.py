from django.urls import path
from . import views

app_name = "detai"

urlpatterns = [
    # Dashboard Trưởng khoa (Sprint 3)
    path("", views.sprint3_dashboard_view, name="dashboard"),
    path("<int:dot_id>/", views.sprint3_dashboard_view, name="dashboard_dot"),
    path("<int:dot_id>/chuyen-sang-thuc-hien/", views.chuyen_sang_thuc_hien_action, name="chuyen_sang_thuc_hien"),

    # Ngân hàng đề tài gợi ý của GVHD (UC12)
    path("tao-goi-y/", views.tao_de_tai_goi_y_action, name="tao_de_tai_goi_y"),
    path("goi-y/<int:gy_id>/doi-trang-thai/", views.doi_trang_thai_goi_y_action, name="doi_trang_thai_goi_y"),

    # Sinh viên chọn hoặc đề xuất đề tài (UC13, UC14)
    path("dang-ky/", views.sinh_vien_dang_ky_de_tai_action, name="sinh_vien_dang_ky"),

    # GVHD thẩm định & chốt đề tài (UC15)
    path("<int:de_tai_id>/phe-duyet/", views.gvhd_phe_duyet_action, name="gvhd_phe_duyet"),
    path("<int:dot_id>/duyet-tat-ca/", views.gvhd_duyet_tat_ca_action, name="gvhd_duyet_tat_ca"),
]
