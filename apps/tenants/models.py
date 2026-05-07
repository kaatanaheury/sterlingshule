"""Multi-tenant root: Institution model."""
import random
import string

from django.db import models

from apps.core.models import TimeStampedModel


def _generate_institution_key() -> str:
    """Generate a 6-digit numeric institution key."""
    return "".join(random.choices(string.digits, k=6))


class Institution(TimeStampedModel):
    """A school / academic institution. Root of tenant isolation."""

    name = models.CharField(max_length=200)
    institution_key = models.CharField(max_length=6, unique=True, db_index=True)

    motto = models.CharField(max_length=255, blank=True)
    vision = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to="institution_logos/", blank=True, null=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} ({self.institution_key})"

    def save(self, *args, **kwargs):
        # Always allocate a unique 6-digit key on create.
        if not self.institution_key:
            for _ in range(100):
                candidate = _generate_institution_key()
                if not Institution.objects.filter(institution_key=candidate).exists():
                    self.institution_key = candidate
                    break
            else:
                raise RuntimeError("Could not allocate a unique institution key.")
        super().save(*args, **kwargs)
