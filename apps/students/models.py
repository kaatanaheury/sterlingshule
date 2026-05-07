"""Student profile linked to a User account."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TenantOwnedModel


class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHER = "O", "Other"


class Student(TenantOwnedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    first_name = models.CharField(max_length=80)
    second_name = models.CharField(max_length=80)
    third_name = models.CharField(max_length=80, blank=True)

    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    class_level = models.ForeignKey(
        "academics.ClassLevel",
        on_delete=models.PROTECT,
        related_name="students",
    )
    stream = models.ForeignKey(
        "academics.Stream",
        on_delete=models.SET_NULL,
        related_name="students",
        null=True,
        blank=True,
    )
    admission_number = models.CharField(max_length=50)

    class Meta:
        ordering = ("class_level", "first_name", "second_name")
        constraints = [
            models.UniqueConstraint(
                fields=("institution", "admission_number"),
                name="unique_admission_per_institution",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.second_name} ({self.admission_number})"

    def clean(self):
        super().clean()
        if self.class_level.institution_id != self.institution_id:
            raise ValidationError("Class level must belong to the same institution.")
        if self.stream and self.stream.institution_id != self.institution_id:
            raise ValidationError("Stream must belong to the same institution.")

    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.second_name]
        if self.third_name:
            parts.append(self.third_name)
        return " ".join(parts)
