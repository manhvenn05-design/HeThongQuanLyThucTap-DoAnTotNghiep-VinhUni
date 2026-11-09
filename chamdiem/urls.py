from django.urls import path
from . import views

app_name = "chamdiem"

urlpatterns = [
    path("", views.sprint5_dashboard_view, name="dashboard"),
    path("<int:dot_id>/", views.sprint5_dashboard_view, name="dashboard_dot"),
]
