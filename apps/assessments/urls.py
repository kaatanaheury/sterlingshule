from django.urls import path

from . import views

app_name = "assessments"

urlpatterns = [
    path("", views.assessment_list, name="list"),
    path("new/", views.assessment_create, name="create"),
    path("<int:pk>/edit/", views.assessment_edit, name="edit"),
    path("<int:pk>/rubric/", views.assessment_edit_rubric, name="edit_rubric"),
    path("<int:pk>/lock/", views.assessment_toggle_lock, name="toggle_lock"),
    path("<int:pk>/delete/", views.assessment_delete, name="delete"),
    path("<int:pk>/marks/", views.assessment_pick_class, name="pick_class"),
    path("<int:pk>/marks/entry/", views.marks_entry, name="marks_entry"),
]
