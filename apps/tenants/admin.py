from django.contrib import admin

from .models import Institution
from .models_extras import InstitutionBootstrapCredentials


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "institution_key", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "institution_key", "email")
    readonly_fields = ("institution_key", "created_at", "updated_at")
    fieldsets = (
        ("Identity", {
            "fields": ("name", "institution_key", "is_active"),
        }),
        ("Branding & Vision", {
            "fields": ("motto", "vision", "logo"),
        }),
        ("Contact", {
            "fields": ("address", "phone", "email"),
        }),
        ("Audit", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(InstitutionBootstrapCredentials)
class InstitutionBootstrapCredentialsAdmin(admin.ModelAdmin):
    """
    Lets the Global Admin read the auto-generated ICT Admin temp credentials
    so they can hand them off to the school.
    """

    list_display = ("institution", "username", "temporary_password", "delivered", "created_at")
    list_filter = ("delivered",)
    readonly_fields = ("institution", "username", "temporary_password", "created_at", "updated_at")
    list_editable = ("delivered",)
    search_fields = ("institution__name", "username")
