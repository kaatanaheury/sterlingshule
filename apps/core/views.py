"""Core views: landing page, dashboard, theme toggle, healthcheck."""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def healthz(request):
    return HttpResponse("ok", content_type="text/plain")


def landing(request):
    """Minimalistic landing page for unauthenticated users."""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("core:dashboard"))
    return render(request, "core/landing.html")


@login_required
def dashboard(request):
    user = request.user
    context = {
        "user": user,
        "role_label": user.get_role_display() if hasattr(user, "get_role_display") else "User",
        "institution": getattr(request, "institution", None),
    }
    return render(request, "core/dashboard.html", context)


def toggle_theme(request):
    """Flip between light/dark and remember it via cookie."""
    current = request.COOKIES.get("ss_theme", "light")
    new_theme = "dark" if current == "light" else "light"
    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or reverse("core:dashboard")
    response = HttpResponseRedirect(next_url)
    response.set_cookie(
        "ss_theme",
        new_theme,
        max_age=60 * 60 * 24 * 365,
        samesite="Lax",
    )
    return response
