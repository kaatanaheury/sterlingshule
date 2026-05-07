"""Shared admin site configuration."""
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse


class SuperUserOnlyAdminSite(admin.AdminSite):
    """
    Custom admin site that requires superuser status.
    Only Global Admins (Django superusers) can access /admin/.
    """

    site_header = "SterlingShule Admin (Global Admin Only)"

    def has_permission(self, request):
        """Allow access only if user is a superuser."""
        return request.user.is_active and request.user.is_superuser

    def index(self, request, extra_context=None):
        """Enforce superuser check on admin index."""
        if not self.has_permission(request):
            # Redirect non-superusers away from admin
            return HttpResponseRedirect(reverse("accounts:login"))
        return super().index(request, extra_context)
