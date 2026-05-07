"""Forms for the Academics module."""
from django import forms

from .models import ClassLevel, Department, Session, Stream, Subject


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ("name", "opening_date", "closing_date", "is_active")
        widgets = {
            "opening_date": forms.DateInput(attrs={"type": "date"}),
            "closing_date": forms.DateInput(attrs={"type": "date"}),
        }


class ClassLevelForm(forms.ModelForm):
    class Meta:
        model = ClassLevel
        fields = ("name", "order")


class StreamForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = ("class_level", "name")

    def __init__(self, *args, institution=None, **kwargs):
        super().__init__(*args, **kwargs)
        if institution is not None:
            self.fields["class_level"].queryset = ClassLevel.objects.filter(
                institution=institution
            )


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ("name", "code")


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ("name", "head", "members")

    def __init__(self, *args, institution=None, **kwargs):
        super().__init__(*args, **kwargs)
        if institution is not None:
            from apps.teachers.models import Teacher
            qs = Teacher.objects.filter(institution=institution)
            self.fields["head"].queryset = qs
            self.fields["members"].queryset = qs
            self.fields["members"].widget = forms.SelectMultiple(
                attrs={"size": "6"}
            )
