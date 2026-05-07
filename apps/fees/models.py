"""Fees: structures, per-student liability, payments."""
from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.models import TenantOwnedModel


class FeeStructure(TenantOwnedModel):
    """A fee structure that applies to one or more class levels for a given session."""

    session = models.ForeignKey(
        "academics.Session", on_delete=models.PROTECT, related_name="fee_structures"
    )
    name = models.CharField(max_length=120)
    applies_to_class_levels = models.ManyToManyField(
        "academics.ClassLevel",
        related_name="fee_structures",
        blank=True,
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.name} · {self.session.name}"


class StudentFee(TenantOwnedModel):
    """Per-student fee liability — required amount and running balance."""

    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="fees"
    )
    fee_structure = models.ForeignKey(
        FeeStructure, on_delete=models.PROTECT, related_name="student_fees"
    )
    required_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("student", "fee_structure"),
                name="unique_student_fee",
            ),
        ]

    @property
    def balance(self) -> Decimal:
        return (self.required_amount or Decimal("0.00")) - (self.paid_amount or Decimal("0.00"))

    def __str__(self) -> str:
        return f"{self.student} · {self.fee_structure.name}"


class Payment(TenantOwnedModel):
    student_fee = models.ForeignKey(
        StudentFee, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_payments",
    )

    class Meta:
        ordering = ("-paid_at",)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recompute paid_amount for the parent StudentFee.
        sf = self.student_fee
        total = sum((p.amount for p in sf.payments.all()), Decimal("0.00"))
        sf.paid_amount = total
        sf.save(update_fields=["paid_amount", "updated_at"])

    def __str__(self) -> str:
        return f"{self.student_fee.student} · {self.amount}"
