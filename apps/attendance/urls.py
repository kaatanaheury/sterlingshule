from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path("", views.attendance_overview, name="overview"),
    path("mark/", views.mark_attendance, name="mark"),
]
