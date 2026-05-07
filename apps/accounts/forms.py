"""Account-related forms."""
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import SetPasswordForm


class InstitutionLoginForm(forms.Form):
    """Login with Institution Key + username + password."""

    institution_key = forms.CharField(
        label="Institution Key",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            "placeholder": "6-digit key",
            "autocomplete": "off",
            "inputmode": "numeric",
        }),
    )
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "username"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        institution_key = (cleaned.get("institution_key") or "").strip()
        username = (cleaned.get("username") or "").strip()
        password = cleaned.get("password")

        if institution_key and username and password:
            user = authenticate(
                self.request,
                username=username,
                password=password,
                institution_key=institution_key,
            )
            if user is None:
                raise forms.ValidationError(
                    "Invalid Institution Key, username or password."
                )
            self.user_cache = user
        return cleaned

    def get_user(self):
        return self.user_cache


class FirstLoginPasswordChangeForm(SetPasswordForm):
    """Plain SetPasswordForm — clears must_change_password on save."""

    def save(self, commit=True):
        user = super().save(commit=False)
        user.must_change_password = False
        if commit:
            user.save()
        return user
