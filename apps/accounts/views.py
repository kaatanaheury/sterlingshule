"""Auth views: login, logout, force-change password."""
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import FirstLoginPasswordChangeForm, InstitutionLoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        form = InstitutionLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.must_change_password:
                messages.info(request, "Please set a new password to continue.")
                return redirect("accounts:change_password")
            return redirect("core:dashboard")
    else:
        form = InstitutionLoginForm(request)

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("accounts:login")


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = FirstLoginPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password updated successfully.")
            return redirect("core:dashboard")
    else:
        form = FirstLoginPasswordChangeForm(user=request.user)

    return render(request, "accounts/change_password.html", {"form": form})
