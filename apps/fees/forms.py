"""Fee forms."""
from decimal import Decimal

from django import forms

from apps.academics.models import ClassLevel, Session
from apps.students.models import Student

from .models import FeeStructure, Payment, StudentFee


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ("session", "name", "applies_to_class_levels", "total_amount")
        widgets = {"applies_to_class_levels": forms.CheckboxSelectMultiple()}

    def __init__(self, *args, institution=None, **kwargs):
        super().__init__(*args, **kwargs)
        if institution is not None:
            self.fields["session"].queryset = Session.objects.filter(institution=institution)
            self.fields["applies_to_class_levels"].queryset = ClassLevel.objects.filter(
                institution=institution
            )


class StudentFeeForm(forms.ModelForm):
    class Meta:
        model = StudentFee
        fields = ("student", "fee_structure", "required_amount")

    def __init__(self, *args, institution=None, **kwargs):
        super().__init__(*args, **kwargs)
        if institution is not None:
            self.fields["student"].queryset = Student.objects.filter(institution=institution)
            self.fields["fee_structure"].queryset = FeeStructure.objects.filter(
                institution=institution
            )


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("amount", "method", "reference", "notes")
