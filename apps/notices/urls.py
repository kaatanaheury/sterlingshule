from django.urls import path

from . import views

app_name = "notices"

urlpatterns = [
    path("", views.notice_list, name="list"),
    path("new/", views.notice_create, name="create"),
    path("<int:pk>/edit/", views.notice_edit, name="edit"),
    path("<int:pk>/delete/", views.notice_delete, name="delete"),
]
