"""Forms for the Students module."""
from django import forms

from apps.academics.models import ClassLevel, Stream

from .models import Student


class StudentForm(forms.ModelForm):
    """Create/edit a Student. The User account is auto-created on save."""

    initial_password = forms.CharField(
        required=False,
        label="Initial password",
        help_text="If left blank, the admission number is used. The student will be asked to change it on first login.",
    )

    class Meta:
        model = Student
        fields = (
            "first_name",
            "second_name",
            "third_name",
            "gender",
            "date_of_birth",
            "class_level",
            "stream",
            "admission_number",
        )
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, institution=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.institution = institution
        if institution is not None:
            self.fields["class_level"].queryset = ClassLevel.objects.filter(
                institution=institution
            )
            self.fields["stream"].queryset = Stream.objects.filter(institution=institution)
            self.fields["stream"].required = False


class BulkUploadForm(forms.Form):
    """Upload an .xlsx or .csv file with student rows."""

    file = forms.FileField(
        label="CSV or Excel file",
        help_text=(
            "Required columns: first_name, second_name, admission_number, class_level. "
            "Optional: third_name, gender (M/F/O), date_of_birth (YYYY-MM-DD), stream."
        ),
    )
