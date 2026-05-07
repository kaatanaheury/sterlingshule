from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdminCustom(UserAdmin):
    list_display = ("username", "role", "institution", "is_active", "must_change_password")
    list_filter = ("role", "institution", "is_active", "must_change_password")
    search_fields = ("username", "email", "first_name", "last_name", "institution__name")
    fieldsets = UserAdmin.fieldsets + (
        ("School Role", {"fields": ("role", "institution", "must_change_password")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("School Role", {"fields": ("role", "institution", "must_change_password")}),
    )
