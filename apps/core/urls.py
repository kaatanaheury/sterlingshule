from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("healthz", views.healthz, name="healthz"),
    path("theme/toggle/", views.toggle_theme, name="toggle_theme"),
]
