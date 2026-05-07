from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    path("", views.student_list, name="list"),
    path("new/", views.student_create, name="create"),
    path("upload/", views.student_bulk_upload, name="bulk_upload"),
    path("<int:pk>/edit/", views.student_edit, name="edit"),
    path("<int:pk>/delete/", views.student_delete, name="delete"),
]
