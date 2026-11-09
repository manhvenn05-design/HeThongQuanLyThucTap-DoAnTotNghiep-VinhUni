from django.urls import path
from . import views

app_name = "detai"

urlpatterns = [
    path("", views.sprint3_dashboard_view, name="dashboard"),
    path("<int:dot_id>/", views.sprint3_dashboard_view, name="dashboard_dot"),
]
