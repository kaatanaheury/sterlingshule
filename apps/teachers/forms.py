"""Forms for the Teachers module."""
from django import forms

from apps.academics.models import ClassLevel, Session, Stream, Subject

from .models import Teacher, TeacherSubjectAssignment


class TeacherForm(forms.ModelForm):
    role = forms.ChoiceField(
        label="Role",
        choices=(
            ("CLASS_TEACHER", "Class Teacher"),
            ("SUBJECT_TEACHER", "Subject Teacher"),
            ("PRINCIPAL", "Principal"),
        ),
    )
    initial_password = forms.CharField(
        required=False,
        label="Initial password",
        help_text="If left blank, the teacher_id is used. They will be asked to change it on first login.",
    )

    class Meta:
        model = Teacher
        fields = (
            "first_name",
            "second_name",
            "third_name",
            "teacher_id",
            "phone",
            "email",
            "class_teacher_of_class",
            "class_teacher_of_stream",
        )

    def __init__(self, *args, institution=None, **kwargs):
        super().__init__(*args, **kwargs)
        if institution is not None:
            self.fields["class_teacher_of_class"].queryset = ClassLevel.objects.filter(
                institution=institution
            )
            self.fields["class_teacher_of_class"].required = False
            self.fields["class_teacher_of_stream"].queryset = Stream.objects.filter(
                institution=institution
            )
            self.fields["class_teacher_of_stream"].required = False


class BulkUploadTeachersForm(forms.Form):
    file = forms.FileField(
        label="CSV or Excel file",
        help_text="Required: first_name, second_name, teacher_id. Optional: third_name, phone, email, role (CLASS_TEACHER/SUBJECT_TEACHER/PRINCIPAL).",
    )


class TeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherSubjectAssignment
        fields = ("teacher", "subject", "class_level", "stream", "session")

    def __init__(self, *args, institution=None, **kwargs):
        super().__init__(*args, **kwargs)
        if institution is not None:
            self.fields["teacher"].queryset = Teacher.objects.filter(institution=institution)
            self.fields["subject"].queryset = Subject.objects.filter(institution=institution)
            self.fields["class_level"].queryset = ClassLevel.objects.filter(institution=institution)
            self.fields["stream"].queryset = Stream.objects.filter(institution=institution)
            self.fields["stream"].required = False
            self.fields["session"].queryset = Session.objects.filter(institution=institution)
            self.fields["session"].required = False
