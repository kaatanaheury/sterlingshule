from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_index, name="index"),
    path("pdf/<int:assessment_id>/<int:student_id>/", views.report_card_pdf, name="pdf"),
]
