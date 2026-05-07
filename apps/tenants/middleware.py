"""Attach the request user's Institution to every request."""
from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    """
    Sets request.institution to the authenticated user's institution.

    Global Admins (Django superusers) have no institution and are expected to
    work through the Django admin interface.
    """

    def process_request(self, request):
        request.institution = None
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            inst = getattr(user, "institution", None)
            if inst is not None:
                request.institution = inst
        return None
