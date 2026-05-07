"""Notices / announcements with flexible targeting."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantOwnedModel


class LearnerScope(models.TextChoices):
    NONE = "NONE", "Not for learners"
    ALL = "ALL", "All learners"
    CLASS = "CLASS", "Specific class"
    STREAM = "STREAM", "Specific stream"
    STUDENT = "STUDENT", "Specific student"


class StaffScope(models.TextChoices):
    NONE = "NONE", "Not for staff"
    ALL = "ALL", "All staff"
    DEPARTMENT = "DEPARTMENT", "Specific department"
    STAFF = "STAFF", "Specific staff member"


class Notice(TenantOwnedModel):
    title = models.CharField(max_length=200)
    body = models.TextField()
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="notices_posted",
    )

    learner_scope = models.CharField(
        max_length=10, choices=LearnerScope.choices, default=LearnerScope.NONE
    )
    target_class = models.ForeignKey(
        "academics.ClassLevel", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="targeted_notices",
    )
    target_stream = models.ForeignKey(
        "academics.Stream", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="targeted_notices",
    )
    target_student = models.ForeignKey(
        "students.Student", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="targeted_notices",
    )

    staff_scope = models.CharField(
        max_length=12, choices=StaffScope.choices, default=StaffScope.NONE
    )
    target_department = models.ForeignKey(
        "academics.Department", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="targeted_notices",
    )
    target_staff = models.ForeignKey(
        "teachers.Teacher", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="targeted_notices",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title
