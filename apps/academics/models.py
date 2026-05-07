"""Academic structure: sessions, classes, streams, subjects, departments."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import TenantOwnedModel, TimeStampedModel


# ---------------------------------------------------------------------------
# Sessions / Academic Terms
# ---------------------------------------------------------------------------
class Session(TenantOwnedModel):
    name = models.CharField(max_length=100)  # e.g. "Term 1 2026"
    opening_date = models.DateField(null=True, blank=True)
    closing_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("institution", "name"),
                name="unique_session_name_per_institution",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Enforce single-active-session per institution.
        if self.is_active:
            (
                Session.objects.filter(institution=self.institution)
                .exclude(pk=self.pk)
                .update(is_active=False)
            )

    @classmethod
    def active_for(cls, institution):
        return cls.objects.filter(institution=institution, is_active=True).first()


# ---------------------------------------------------------------------------
# ClassLevel (Grade) and Stream
# ---------------------------------------------------------------------------
class ClassLevel(TenantOwnedModel):
    """A grade or class — e.g. 'Grade 1', 'Grade 2'."""

    name = models.CharField(max_length=50)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "name")
        constraints = [
            models.UniqueConstraint(
                fields=("institution", "name"),
                name="unique_classlevel_per_institution",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Stream(TenantOwnedModel):
    """An optional sub-division of a class — e.g. 'Grade 1 Blue'."""

    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.CASCADE,
        related_name="streams",
    )
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ("class_level__order", "name")
        constraints = [
            models.UniqueConstraint(
                fields=("class_level", "name"),
                name="unique_stream_per_class",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.class_level.name} {self.name}"


# ---------------------------------------------------------------------------
# Subjects
# ---------------------------------------------------------------------------
class Subject(TenantOwnedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=16, blank=True)

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("institution", "name"),
                name="unique_subject_name_per_institution",
            ),
        ]

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------
class Department(TenantOwnedModel):
    name = models.CharField(max_length=100)
    head = models.ForeignKey(
        "teachers.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments",
    )
    members = models.ManyToManyField(
        "teachers.Teacher",
        related_name="departments",
        blank=True,
    )

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("institution", "name"),
                name="unique_department_per_institution",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self):
        super().clean()
        if self.head and self.head.institution_id != self.institution_id:
            raise ValidationError("Head of Department must belong to the same institution.")
