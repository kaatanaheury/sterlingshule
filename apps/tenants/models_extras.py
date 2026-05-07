"""Auxiliary tenant-related models kept in a separate module to avoid signal cycles."""
from django.db import models

from apps.core.models import TimeStampedModel


class InstitutionBootstrapCredentials(TimeStampedModel):
    """
    One-off record of the auto-generated ICT Admin temp credentials.
    Visible only to Global Admins via the Django admin.
    Once the ICT Admin changes their password this row is informational only.
    """

    institution = models.OneToOneField(
        "tenants.Institution",
        on_delete=models.CASCADE,
        related_name="bootstrap_credentials",
    )
    username = models.CharField(max_length=150)
    temporary_password = models.CharField(max_length=128)
    delivered = models.BooleanField(
        default=False,
        help_text="Mark when these credentials have been handed over to the ICT Admin.",
    )

    class Meta:
        verbose_name = "Institution bootstrap credentials"
        verbose_name_plural = "Institution bootstrap credentials"

    def __str__(self) -> str:
        return f"Bootstrap creds for {self.institution.name}"
