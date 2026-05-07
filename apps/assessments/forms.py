"""Forms for Assessments and Marks."""
from django import forms
from django.forms import inlineformset_factory

from apps.academics.models import ClassLevel, Session, Stream

from .models import Assessment, Mark, RubricLevel


# Default 8-level CBC rubric — used when a new assessment is created.
DEFAULT_RUBRIC = [
    ("EE 2", 90, 100, 8),
    ("EE 1", 80, 89,  7),
    ("ME 2", 70, 79,  6),
    ("ME 1", 60, 69,  5),
    ("AE 2", 50, 59,  4),
    ("AE 1", 40, 49,  3),
    ("BE 2", 30, 39,  2),
    ("BE 1", 0,  29,  1),
]


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ("session", "name", "max_marks", "target_class_levels", "target_streams")
        widgets = {
            "target_class_levels": forms.CheckboxSelectMultiple(),
            "target_streams": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, institution=None, **kwargs):
        super().__init__(*args, **kwargs)
        if institution is not None:
            self.fields["session"].queryset = Session.objects.filter(institution=institution)
            self.fields["target_class_levels"].queryset = ClassLevel.objects.filter(
                institution=institution
            )
            self.fields["target_streams"].queryset = Stream.objects.filter(institution=institution)
            self.fields["target_streams"].required = False


RubricFormSet = inlineformset_factory(
    Assessment,
    RubricLevel,
    fields=("label", "min_marks", "max_marks", "points", "order"),
    extra=8,
    can_delete=True,
)


class MarkEntryForm(forms.Form):
    """A single hidden form used to drive the bulk marks entry table.

    Actual processing parses POST keys directly: `mark_<student_id>`.
    """
