"""Assessments, customisable rubrics, and student marks."""
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TenantOwnedModel


class Assessment(TenantOwnedModel):
    """An assessment event (CAT 1, Mid-Term, End-Term, etc.)."""

    session = models.ForeignKey(
        "academics.Session",
        on_delete=models.PROTECT,
        related_name="assessments",
    )
    name = models.CharField(max_length=120)
    target_class_levels = models.ManyToManyField(
        "academics.ClassLevel",
        related_name="assessments",
        blank=True,
    )
    target_streams = models.ManyToManyField(
        "academics.Stream",
        related_name="assessments",
        blank=True,
    )
    max_marks = models.PositiveIntegerField(default=100)
    is_locked = models.BooleanField(
        default=False,
        help_text="When locked, marks cannot be edited.",
    )

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("institution", "session", "name"),
                name="unique_assessment_per_session",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.session.name})"

    def compute_for(self, marks):
        """Given a numeric mark, return the matching (points, rubric_label)."""
        levels = list(self.rubric_levels.order_by("min_marks"))
        for lvl in levels:
            if lvl.min_marks <= marks <= lvl.max_marks:
                return (lvl.points, lvl.label)
        return (0, "")


class RubricLevel(TenantOwnedModel):
    """Editable 8-level rubric attached to an assessment."""

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="rubric_levels",
    )
    label = models.CharField(max_length=50)  # e.g. EE 1, ME 2, AE 1, BE 1
    min_marks = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2)
    points = models.PositiveSmallIntegerField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("assessment", "order")

    def __str__(self) -> str:
        return f"{self.assessment.name} · {self.label} ({self.min_marks}-{self.max_marks})"

    def clean(self):
        super().clean()
        if self.min_marks > self.max_marks:
            raise ValidationError("min_marks must be ≤ max_marks.")


class Mark(TenantOwnedModel):
    """A subject mark for one student in one assessment."""

    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="marks"
    )
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="marks"
    )
    subject = models.ForeignKey(
        "academics.Subject", on_delete=models.PROTECT, related_name="marks"
    )
    teacher = models.ForeignKey(
        "teachers.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entered_marks",
    )

    marks = models.DecimalField(max_digits=5, decimal_places=2)
    points = models.PositiveSmallIntegerField(default=0)
    rubric_label = models.CharField(max_length=50, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("assessment", "student", "subject"),
                name="unique_mark_per_assessment_student_subject",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.student} · {self.subject} · {self.marks}"

    def save(self, *args, **kwargs):
        # Auto-calculate points and rubric from the assessment's rubric levels.
        if self.assessment_id and self.marks is not None:
            pts, label = self.assessment.compute_for(self.marks)
            self.points = pts
            self.rubric_label = label
        super().save(*args, **kwargs)
