"""Daily attendance per class/stream."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantOwnedModel


class AttendanceStatus(models.TextChoices):
    PRESENT = "P", "Present"
    ABSENT = "A", "Absent"
    LATE = "L", "Late"


class AttendanceDay(TenantOwnedModel):
    """One per class/stream per day."""

    date = models.DateField()
    class_level = models.ForeignKey(
        "academics.ClassLevel", on_delete=models.CASCADE, related_name="attendance_days"
    )
    stream = models.ForeignKey(
        "academics.Stream",
        on_delete=models.CASCADE,
        related_name="attendance_days",
        null=True,
        blank=True,
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_days",
    )

    class Meta:
        ordering = ("-date",)
        constraints = [
            models.UniqueConstraint(
                fields=("institution", "date", "class_level", "stream"),
                name="unique_attendance_day",
            ),
        ]

    def __str__(self) -> str:
        target = self.stream or self.class_level
        return f"{target} · {self.date}"


class StudentAttendance(TenantOwnedModel):
    attendance_day = models.ForeignKey(
        AttendanceDay, on_delete=models.CASCADE, related_name="entries"
    )
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="attendance_entries"
    )
    status = models.CharField(
        max_length=1,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
    )
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("attendance_day", "student"),
                name="unique_attendance_entry",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.student} · {self.attendance_day.date} · {self.get_status_display()}"
