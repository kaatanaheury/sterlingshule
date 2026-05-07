"""Teachers views — list, create, edit, delete, bulk upload, subject assignments."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import Role

from .forms import BulkUploadTeachersForm, TeacherAssignmentForm, TeacherForm
from .models import Teacher, TeacherSubjectAssignment
from .services import create_teacher_with_user, import_teachers


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def teacher_list(request):
    teachers = Teacher.objects.filter(institution=request.institution).select_related("user")
    return render(request, "teachers/list.html", {"teachers": teachers})


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def teacher_create(request):
    if request.method == "POST":
        form = TeacherForm(request.POST, institution=request.institution)
        if form.is_valid():
            teacher = create_teacher_with_user(
                institution=request.institution,
                first_name=form.cleaned_data["first_name"],
                second_name=form.cleaned_data["second_name"],
                third_name=form.cleaned_data.get("third_name") or "",
                teacher_id=form.cleaned_data["teacher_id"],
                phone=form.cleaned_data.get("phone") or "",
                email=form.cleaned_data.get("email") or "",
                role=form.cleaned_data.get("role") or Role.SUBJECT_TEACHER,
                initial_password=form.cleaned_data.get("initial_password") or None,
                class_teacher_of_class=form.cleaned_data.get("class_teacher_of_class"),
                class_teacher_of_stream=form.cleaned_data.get("class_teacher_of_stream"),
            )
            messages.success(
                request,
                f"Teacher '{teacher.full_name}' added. Login: {teacher.user.username} / "
                f"{form.cleaned_data.get('initial_password') or teacher.teacher_id}",
            )
            return redirect("teachers:list")
    else:
        form = TeacherForm(institution=request.institution)
    return render(
        request,
        "teachers/form_page.html",
        {"form": form, "title": "Add new teacher"},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk, institution=request.institution)
    if request.method == "POST":
        form = TeacherForm(request.POST, instance=teacher, institution=request.institution)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.save()
            # Sync user role + display name
            new_role = form.cleaned_data.get("role")
            if new_role:
                teacher.user.role = new_role
            teacher.user.first_name = obj.first_name
            teacher.user.last_name = obj.second_name
            teacher.user.save(update_fields=["role", "first_name", "last_name"])
            messages.success(request, "Teacher updated.")
            return redirect("teachers:list")
    else:
        form = TeacherForm(instance=teacher, institution=request.institution, initial={"role": teacher.user.role})
        form.fields["initial_password"].widget = form.fields["initial_password"].hidden_widget()
    return render(
        request,
        "teachers/form_page.html",
        {"form": form, "title": f"Edit {teacher.full_name}"},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk, institution=request.institution)
    if request.method == "POST":
        username = teacher.user.username
        teacher.user.delete()
        messages.success(request, f"Teacher '{username}' deleted.")
        return redirect("teachers:list")
    return render(request, "teachers/confirm_delete.html", {"teacher": teacher})


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def teacher_bulk_upload(request):
    result = None
    if request.method == "POST":
        form = BulkUploadTeachersForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                result = import_teachers(
                    institution=request.institution,
                    uploaded_file=form.cleaned_data["file"],
                )
                messages.success(request, f"Imported {result['created']} teacher(s).")
            except Exception as exc:
                messages.error(request, f"Failed to read the file: {exc}")
    else:
        form = BulkUploadTeachersForm()
    return render(request, "teachers/bulk_upload.html", {"form": form, "result": result})


# ---- Subject assignments ----
@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def assignment_list(request):
    rows = TeacherSubjectAssignment.objects.filter(
        institution=request.institution
    ).select_related("teacher", "subject", "class_level", "stream", "session")
    return render(request, "teachers/assignments_list.html", {"assignments": rows})


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def assignment_create(request):
    if request.method == "POST":
        form = TeacherAssignmentForm(request.POST, institution=request.institution)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.save()
            messages.success(request, "Assignment saved.")
            return redirect("teachers:assignment_list")
    else:
        form = TeacherAssignmentForm(institution=request.institution)
    return render(
        request,
        "teachers/assignment_form.html",
        {"form": form, "title": "New subject assignment"},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def assignment_delete(request, pk):
    obj = get_object_or_404(
        TeacherSubjectAssignment, pk=pk, institution=request.institution
    )
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Assignment removed.")
        return redirect("teachers:assignment_list")
    return render(
        request,
        "teachers/assignment_confirm_delete.html",
        {"assignment": obj},
    )
