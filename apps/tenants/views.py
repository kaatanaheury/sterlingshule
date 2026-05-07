"""Settings views for the ICT Admin (school logo, motto, etc.)."""
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import Role

from .models import Institution


class InstitutionSettingsForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ("name", "motto", "vision", "address", "phone", "email", "logo")
        widgets = {
            "vision": forms.Textarea(attrs={"rows": 3}),
        }


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def institution_settings(request):
    institution = request.institution
    if institution is None:
        messages.error(request, "No institution context.")
        return redirect("core:dashboard")

    if request.method == "POST":
        form = InstitutionSettingsForm(request.POST, request.FILES, instance=institution)
        if form.is_valid():
            form.save()
            messages.success(request, "Institution settings updated.")
            return redirect("tenants:settings")
    else:
        form = InstitutionSettingsForm(instance=institution)

    return render(request, "tenants/settings.html", {"form": form, "institution": institution})
