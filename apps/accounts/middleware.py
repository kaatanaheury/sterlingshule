"""
Force users with `must_change_password=True` to change their password before
accessing any other view.
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


# Paths that are always allowed even for users that must change their password.
_EXEMPT_PATH_PREFIXES = (
    "/accounts/change-password",
    "/accounts/logout",
    "/accounts/login",
    "/static/",
    "/media/",
    "/admin/",
    "/healthz",
)


class ForcePasswordChangeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return None
        if not getattr(user, "must_change_password", False):
            return None
        path = request.path
        for prefix in _EXEMPT_PATH_PREFIXES:
            if path.startswith(prefix):
                return None
        return redirect(reverse("accounts:change_password"))
