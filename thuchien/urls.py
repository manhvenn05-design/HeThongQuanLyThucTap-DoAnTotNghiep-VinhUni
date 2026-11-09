from django.urls import path
from . import views

app_name = "thuchien"

urlpatterns = [
    path("", views.sprint4_dashboard_view, name="dashboard"),
    path("<int:dot_id>/", views.sprint4_dashboard_view, name="dashboard_dot"),
]
