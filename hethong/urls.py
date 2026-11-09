from django.urls import path
from . import views

app_name = "hethong"

urlpatterns = [
    path("", views.sprint6_dashboard_view, name="dashboard"),
    path("sprint6/", views.sprint6_dashboard_view, name="sprint6_dashboard"),
    path("<int:dot_id>/", views.sprint6_dashboard_view, name="sprint6_dashboard_dot"),
    path("tongket/", views.sprint6_dashboard_view, name="sprint6_tongket"),
    path("quantri/", views.quantri_view, name="quantri"),
]
