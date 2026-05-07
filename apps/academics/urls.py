from django.urls import path

from . import views

app_name = "academics"

urlpatterns = [
    path("", views.academics_overview, name="overview"),

    path("sessions/", views.session_list, name="session_list"),
    path("sessions/new/", views.session_create, name="session_create"),
    path("sessions/<int:pk>/edit/", views.session_edit, name="session_edit"),
    path("sessions/<int:pk>/activate/", views.session_activate, name="session_activate"),
    path("sessions/<int:pk>/delete/", views.session_delete, name="session_delete"),

    path("classes/", views.classlevel_list, name="classlevel_list"),
    path("classes/new/", views.classlevel_create, name="classlevel_create"),
    path("classes/<int:pk>/edit/", views.classlevel_edit, name="classlevel_edit"),
    path("classes/<int:pk>/delete/", views.classlevel_delete, name="classlevel_delete"),

    path("streams/", views.stream_list, name="stream_list"),
    path("streams/new/", views.stream_create, name="stream_create"),
    path("streams/<int:pk>/edit/", views.stream_edit, name="stream_edit"),
    path("streams/<int:pk>/delete/", views.stream_delete, name="stream_delete"),

    path("subjects/", views.subject_list, name="subject_list"),
    path("subjects/new/", views.subject_create, name="subject_create"),
    path("subjects/<int:pk>/edit/", views.subject_edit, name="subject_edit"),
    path("subjects/<int:pk>/delete/", views.subject_delete, name="subject_delete"),

    path("departments/", views.department_list, name="department_list"),
    path("departments/new/", views.department_create, name="department_create"),
    path("departments/<int:pk>/edit/", views.department_edit, name="department_edit"),
    path("departments/<int:pk>/delete/", views.department_delete, name="department_delete"),
]
