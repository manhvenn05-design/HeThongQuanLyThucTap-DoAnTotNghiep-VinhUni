"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from hethong.views import quantri_view
from organization.views import giangvien_portal_view, sinhvien_portal_view
from accounts.views import login_view, logout_view
from dots.views import switch_dot_view
from hoso.views import (
    sprint1_dashboard,
    upload_excel_view,
    preview_excel_view,
    confirm_excel_view,
    sync_usmart_view,
    advance_phase_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # MẶC ĐỊNH KHI VỪA CHẠY HỆ THỐNG: LUÔN LUÔN VÀO TRANG ĐĂNG NHẬP ĐẦU TIÊN
    path('', login_view, name='root_login'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Sprint 1 (CHUAN_BI) routes (Bảng điều khiển Trưởng khoa)
    path('sprint1/', sprint1_dashboard, name='sprint1_dashboard'),
    path('dots/switch/<int:dot_id>/', switch_dot_view, name='switch_dot'),
    path('dot/<int:dot_id>/', sprint1_dashboard, name='sprint1_dashboard_dot'),
    path('dot/<int:dot_id>/upload-excel/', upload_excel_view, name='upload_excel'),
    path('import/<int:lan_nhap_id>/preview/', preview_excel_view, name='preview_excel'),
    path('import/<int:lan_nhap_id>/confirm/', confirm_excel_view, name='confirm_excel'),
    path('dot/<int:dot_id>/sync-usmart/', sync_usmart_view, name='sync_usmart'),
    path('dot/<int:dot_id>/advance-phase/', advance_phase_view, name='advance_phase'),

    # Sprint 2 (PHAN_CONG) routes
    path('phancong/', include('phancong.urls', namespace='phancong')),

    # Sprint 3 (CHOT_DE_TAI) routes
    path('detai/', include('detai.urls', namespace='detai')),

    # Sprint 4 (THUC_HIEN) routes
    path('thuchien/', include('thuchien.urls', namespace='thuchien')),

    # Sprint 5 (CHAM_DIEM) routes
    path('chamdiem/', include('chamdiem.urls', namespace='chamdiem')),

    # Sprint 6 (HOAN_TAT) routes
    path('hoantat/', include('hethong.urls', namespace='hethong')),

    # Quản trị hệ thống (UC02, UC29, UC30)
    path('quantri/', quantri_view, name='quantri'),

    # CỔNG CHUYÊN BIỆT CHO CÁC ACTOR (Role-Based Portals)
    path('giangvien/', giangvien_portal_view, name='giangvien_portal'),
    path('sinhvien/', sinhvien_portal_view, name='sinhvien_portal'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
