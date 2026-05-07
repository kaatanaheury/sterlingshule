from django.urls import path

from . import views

app_name = "fees"

urlpatterns = [
    path("", views.fees_overview, name="overview"),
    path("structures/new/", views.structure_create, name="structure_create"),
    path("structures/<int:pk>/edit/", views.structure_edit, name="structure_edit"),
    path("structures/<int:pk>/apply/", views.structure_apply, name="structure_apply"),
    path("student-fees/new/", views.student_fee_create, name="student_fee_create"),
    path("student-fees/<int:pk>/", views.student_fee_detail, name="student_fee"),
]
