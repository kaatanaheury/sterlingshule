from django.urls import path

from . import views

app_name = "teachers"

urlpatterns = [
    path("", views.teacher_list, name="list"),
    path("new/", views.teacher_create, name="create"),
    path("upload/", views.teacher_bulk_upload, name="bulk_upload"),
    path("<int:pk>/edit/", views.teacher_edit, name="edit"),
    path("<int:pk>/delete/", views.teacher_delete, name="delete"),

    path("assignments/", views.assignment_list, name="assignment_list"),
    path("assignments/new/", views.assignment_create, name="assignment_create"),
    path("assignments/<int:pk>/delete/", views.assignment_delete, name="assignment_delete"),
]
