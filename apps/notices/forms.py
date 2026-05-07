"""Notice forms."""
from django import forms

from apps.academics.models import ClassLevel, Department, Stream
from apps.students.models import Student
from apps.teachers.models import Teacher

from .models import Notice


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = (
            "title",
            "body",
            "learner_scope",
            "target_class",
            "target_stream",
            "target_student",
            "staff_scope",
            "target_department",
            "target_staff",
        )
        widgets = {"body": forms.Textarea(attrs={"rows": 6})}

    def __init__(self, *args, institution=None, **kwargs):
        super().__init__(*args, **kwargs)
        if institution is not None:
            self.fields["target_class"].queryset = ClassLevel.objects.filter(
                institution=institution
            )
            self.fields["target_stream"].queryset = Stream.objects.filter(
                institution=institution
            )
            self.fields["target_student"].queryset = Student.objects.filter(
                institution=institution
            )
            self.fields["target_department"].queryset = Department.objects.filter(
                institution=institution
            )
            self.fields["target_staff"].queryset = Teacher.objects.filter(
                institution=institution
            )
        for fld in (
            "target_class",
            "target_stream",
            "target_student",
            "target_department",
            "target_staff",
        ):
            self.fields[fld].required = False
