"""Shared abstract models."""
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base with created_at / updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantOwnedModel(TimeStampedModel):
    """
    Abstract base for any record that belongs to a single Institution.
    Strict tenant isolation: every concrete subclass MUST set institution.
    """

    institution = models.ForeignKey(
        "tenants.Institution",
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
    )

    class Meta:
        abstract = True
