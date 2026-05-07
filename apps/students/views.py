"""Students views — list, create, edit, delete, bulk upload."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import Role

from .forms import BulkUploadForm, StudentForm
from .models import Student
from .services import create_student_with_user, import_students


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL, Role.CLASS_TEACHER, Role.SUBJECT_TEACHER)
def student_list(request):
    qs = Student.objects.filter(institution=request.institution).select_related(
        "class_level", "stream", "user"
    )
    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(first_name__icontains=q) | qs.filter(
            second_name__icontains=q
        ) | qs.filter(admission_number__icontains=q)
    cl = (request.GET.get("class_level") or "").strip()
    if cl:
        qs = qs.filter(class_level_id=cl)
    from apps.academics.models import ClassLevel
    return render(
        request,
        "students/list.html",
        {
            "students": qs,
            "q": q,
            "selected_class_level": cl,
            "class_levels": ClassLevel.objects.filter(institution=request.institution),
        },
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST, institution=request.institution)
        if form.is_valid():
            student = create_student_with_user(
                institution=request.institution,
                first_name=form.cleaned_data["first_name"],
                second_name=form.cleaned_data["second_name"],
                third_name=form.cleaned_data.get("third_name") or "",
                gender=form.cleaned_data.get("gender") or "",
                date_of_birth=form.cleaned_data.get("date_of_birth"),
                class_level=form.cleaned_data["class_level"],
                stream=form.cleaned_data.get("stream"),
                admission_number=form.cleaned_data["admission_number"],
                initial_password=form.cleaned_data.get("initial_password") or None,
            )
            messages.success(
                request,
                f"Student '{student.full_name}' added. Login: {student.user.username} / "
                f"{form.cleaned_data.get('initial_password') or student.admission_number}",
            )
            return redirect("students:list")
    else:
        form = StudentForm(institution=request.institution)
    return render(
        request,
        "students/form_page.html",
        {"form": form, "title": "Add new student"},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk, institution=request.institution)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student, institution=request.institution)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.save()
            # Sync display name on user
            student.user.first_name = obj.first_name
            student.user.last_name = obj.second_name
            student.user.save(update_fields=["first_name", "last_name"])
            messages.success(request, "Student updated.")
            return redirect("students:list")
    else:
        form = StudentForm(instance=student, institution=request.institution)
        form.fields["initial_password"].widget = form.fields["initial_password"].hidden_widget()
    return render(
        request,
        "students/form_page.html",
        {"form": form, "title": f"Edit {student.full_name}"},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk, institution=request.institution)
    if request.method == "POST":
        username = student.user.username
        student.user.delete()  # cascades to Student
        messages.success(request, f"Student '{username}' deleted.")
        return redirect("students:list")
    return render(
        request,
        "students/confirm_delete.html",
        {"student": student},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def student_bulk_upload(request):
    result = None
    if request.method == "POST":
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                result = import_students(
                    institution=request.institution,
                    uploaded_file=form.cleaned_data["file"],
                )
                messages.success(request, f"Imported {result['created']} student(s).")
            except Exception as exc:
                messages.error(request, f"Failed to read the file: {exc}")
    else:
        form = BulkUploadForm()
    return render(
        request,
        "students/bulk_upload.html",
        {"form": form, "result": result},
    )
