from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("", views.analytics_index, name="index"),
    path("export.pdf", views.analytics_pdf, name="pdf"),
]
