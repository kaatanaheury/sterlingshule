"""SterlingShule URL configuration."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core.admin import SuperUserOnlyAdminSite

# Use custom admin site that requires superuser status
admin.site.__class__ = SuperUserOnlyAdminSite

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("students/", include("apps.students.urls", namespace="students")),
    path("teachers/", include("apps.teachers.urls", namespace="teachers")),
    path("academics/", include("apps.academics.urls", namespace="academics")),
    path("assessments/", include("apps.assessments.urls", namespace="assessments")),
    path("reports/", include("apps.reports.urls", namespace="reports")),
    path("fees/", include("apps.fees.urls", namespace="fees")),
    path("attendance/", include("apps.attendance.urls", namespace="attendance")),
    path("notices/", include("apps.notices.urls", namespace="notices")),
    path("analytics/", include("apps.analytics.urls", namespace="analytics")),
    path("settings/", include("apps.tenants.urls", namespace="tenants")),
    path("", include("apps.core.urls", namespace="core")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
