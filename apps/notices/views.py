"""Notice views — list (filtered by audience), create, edit, delete."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import Role

from .forms import NoticeForm
from .models import LearnerScope, Notice, StaffScope


def _visible_notices(request):
    """Return notices visible to the requesting user."""
    inst = request.institution
    user = request.user
    qs = Notice.objects.filter(institution=inst).select_related(
        "posted_by", "target_class", "target_stream", "target_student", "target_department", "target_staff"
    )
    if user.is_ict_admin or user.is_principal or user.is_superuser:
        return qs

    student = getattr(user, "student_profile", None)
    teacher = getattr(user, "teacher_profile", None)

    learner_q = Q()
    if student is not None:
        learner_q = (
            Q(learner_scope=LearnerScope.ALL)
            | Q(learner_scope=LearnerScope.CLASS, target_class=student.class_level)
            | Q(learner_scope=LearnerScope.STREAM, target_stream=student.stream)
            | Q(learner_scope=LearnerScope.STUDENT, target_student=student)
        )

    staff_q = Q()
    if teacher is not None:
        dept_ids = list(teacher.departments.values_list("id", flat=True))
        staff_q = (
            Q(staff_scope=StaffScope.ALL)
            | Q(staff_scope=StaffScope.DEPARTMENT, target_department_id__in=dept_ids)
            | Q(staff_scope=StaffScope.STAFF, target_staff=teacher)
        )

    return qs.filter(learner_q | staff_q).distinct()


@login_required
def notice_list(request):
    notices = _visible_notices(request)
    return render(request, "notices/list.html", {"notices": notices})


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def notice_create(request):
    if request.method == "POST":
        form = NoticeForm(request.POST, institution=request.institution)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.posted_by = request.user
            obj.save()
            messages.success(request, "Notice posted.")
            return redirect("notices:list")
    else:
        form = NoticeForm(institution=request.institution)
    return render(
        request,
        "notices/form_page.html",
        {"form": form, "title": "New notice"},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def notice_edit(request, pk):
    notice = get_object_or_404(Notice, pk=pk, institution=request.institution)
    if request.method == "POST":
        form = NoticeForm(request.POST, instance=notice, institution=request.institution)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.save()
            messages.success(request, "Notice updated.")
            return redirect("notices:list")
    else:
        form = NoticeForm(instance=notice, institution=request.institution)
    return render(
        request,
        "notices/form_page.html",
        {"form": form, "title": "Edit notice"},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk, institution=request.institution)
    if request.method == "POST":
        notice.delete()
        messages.success(request, "Notice deleted.")
        return redirect("notices:list")
    return render(request, "notices/confirm_delete.html", {"notice": notice})
