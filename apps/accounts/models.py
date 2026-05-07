"""Custom User model with role-based access control."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    GLOBAL_ADMIN = "GLOBAL_ADMIN", "Global Admin"
    ICT_ADMIN = "ICT_ADMIN", "ICT Admin"
    PRINCIPAL = "PRINCIPAL", "Principal"
    CLASS_TEACHER = "CLASS_TEACHER", "Class Teacher"
    SUBJECT_TEACHER = "SUBJECT_TEACHER", "Subject Teacher"
    STUDENT = "STUDENT", "Student"


class User(AbstractUser):
    """
    Username-based authentication. The active session is also scoped to an
    Institution (except for Django superusers / Global Admins).

    For students/teachers the username is set by the ICT Admin (typically the
    first name for students). The InstitutionAuthBackend ensures that the
    correct Institution Key + username + password combination is required.
    """

    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    institution = models.ForeignKey(
        "tenants.Institution",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
        help_text="Null only for Django superusers (Global Admins).",
    )
    must_change_password = models.BooleanField(
        default=False,
        help_text="Forces a password change on next login.",
    )

    class Meta:
        ordering = ("username",)
        # A username is unique per-institution; superusers (no institution)
        # also remain unique by username via Django's default constraint.
        constraints = [
            models.UniqueConstraint(
                fields=("institution", "username"),
                name="unique_username_per_institution",
            ),
        ]

    def __str__(self) -> str:
        if self.institution_id:
            return f"{self.username} @ {self.institution.name}"
        return self.username

    # ----- Convenience role checks -----
    @property
    def is_global_admin(self) -> bool:
        return self.is_superuser or self.role == Role.GLOBAL_ADMIN

    @property
    def is_ict_admin(self) -> bool:
        return self.role == Role.ICT_ADMIN

    @property
    def is_principal(self) -> bool:
        return self.role == Role.PRINCIPAL

    @property
    def is_class_teacher(self) -> bool:
        return self.role == Role.CLASS_TEACHER

    @property
    def is_subject_teacher(self) -> bool:
        return self.role == Role.SUBJECT_TEACHER

    @property
    def is_any_teacher(self) -> bool:
        return self.role in (Role.CLASS_TEACHER, Role.SUBJECT_TEACHER)

    @property
    def is_student(self) -> bool:
        return self.role == Role.STUDENT

    @property
    def can_post_notices(self) -> bool:
        return self.role in (Role.ICT_ADMIN, Role.PRINCIPAL)
