"""Teacher profile + subject assignments."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TenantOwnedModel


class Teacher(TenantOwnedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )

    first_name = models.CharField(max_length=80)
    second_name = models.CharField(max_length=80)
    third_name = models.CharField(max_length=80, blank=True)

    teacher_id = models.CharField(max_length=50)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)

    # Class teachers can be assigned to a specific class/stream.
    class_teacher_of_class = models.ForeignKey(
        "academics.ClassLevel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_teachers",
    )
    class_teacher_of_stream = models.ForeignKey(
        "academics.Stream",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_teachers",
    )

    class Meta:
        ordering = ("first_name", "second_name")
        constraints = [
            models.UniqueConstraint(
                fields=("institution", "teacher_id"),
                name="unique_teacher_id_per_institution",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.second_name} ({self.teacher_id})"

    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.second_name]
        if self.third_name:
            parts.append(self.third_name)
        return " ".join(parts)

    @property
    def initials(self) -> str:
        names = [self.first_name, self.second_name]
        if self.third_name:
            names.append(self.third_name)
        return "".join(n[:1].upper() for n in names if n)


class TeacherSubjectAssignment(TenantOwnedModel):
    """One assignment = teacher teaches subject in a given class (and optional stream)."""

    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="subject_assignments"
    )
    subject = models.ForeignKey(
        "academics.Subject", on_delete=models.CASCADE, related_name="teacher_assignments"
    )
    class_level = models.ForeignKey(
        "academics.ClassLevel", on_delete=models.CASCADE, related_name="teacher_assignments"
    )
    stream = models.ForeignKey(
        "academics.Stream",
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
        null=True,
        blank=True,
    )
    session = models.ForeignKey(
        "academics.Session",
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("teacher", "subject", "class_level", "stream", "session"),
                name="unique_teacher_subject_assignment",
            ),
        ]

    def __str__(self) -> str:
        target = self.stream or self.class_level
        return f"{self.teacher} → {self.subject} @ {target}"

    def clean(self):
        super().clean()
        for related, label in (
            (self.teacher, "Teacher"),
            (self.subject, "Subject"),
            (self.class_level, "Class level"),
        ):
            if related and related.institution_id != self.institution_id:
                raise ValidationError(f"{label} must belong to the same institution.")
        if self.stream and self.stream.institution_id != self.institution_id:
            raise ValidationError("Stream must belong to the same institution.")
