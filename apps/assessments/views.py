"""Assessments + Marks entry views."""
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.academics.models import Subject
from apps.accounts.decorators import role_required
from apps.accounts.models import Role
from apps.students.models import Student
from apps.teachers.models import Teacher

from .forms import DEFAULT_RUBRIC, AssessmentForm, RubricFormSet
from .models import Assessment, Mark, RubricLevel


# ---------------------------------------------------------------------------
# Assessments CRUD
# ---------------------------------------------------------------------------
@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL, Role.CLASS_TEACHER, Role.SUBJECT_TEACHER)
def assessment_list(request):
    assessments = (
        Assessment.objects.filter(institution=request.institution)
        .select_related("session")
        .prefetch_related("target_class_levels", "target_streams")
    )
    return render(request, "assessments/list.html", {"assessments": assessments})


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def assessment_create(request):
    if request.method == "POST":
        form = AssessmentForm(request.POST, institution=request.institution)
        if form.is_valid():
            with transaction.atomic():
                obj = form.save(commit=False)
                obj.institution = request.institution
                obj.save()
                form.save_m2m()
                # Seed default 8-level rubric
                for order, (label, lo, hi, pts) in enumerate(DEFAULT_RUBRIC, start=1):
                    RubricLevel.objects.create(
                        institution=request.institution,
                        assessment=obj,
                        label=label,
                        min_marks=Decimal(lo),
                        max_marks=Decimal(hi),
                        points=pts,
                        order=order,
                    )
            messages.success(request, "Assessment created with default 8-level rubric.")
            return redirect("assessments:edit_rubric", pk=obj.pk)
    else:
        form = AssessmentForm(institution=request.institution)
    return render(
        request,
        "assessments/form_page.html",
        {"form": form, "title": "New assessment"},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def assessment_edit(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, institution=request.institution)
    if request.method == "POST":
        form = AssessmentForm(request.POST, instance=assessment, institution=request.institution)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.save()
            form.save_m2m()
            messages.success(request, "Assessment updated.")
            return redirect("assessments:list")
    else:
        form = AssessmentForm(instance=assessment, institution=request.institution)
    return render(
        request,
        "assessments/form_page.html",
        {"form": form, "title": f"Edit {assessment.name}"},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def assessment_edit_rubric(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, institution=request.institution)
    if request.method == "POST":
        formset = RubricFormSet(request.POST, instance=assessment)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for obj in instances:
                obj.institution = request.institution
                obj.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, "Rubric saved.")
            return redirect("assessments:list")
    else:
        formset = RubricFormSet(instance=assessment)
    return render(
        request,
        "assessments/edit_rubric.html",
        {"assessment": assessment, "formset": formset},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def assessment_toggle_lock(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, institution=request.institution)
    assessment.is_locked = not assessment.is_locked
    assessment.save(update_fields=["is_locked", "updated_at"])
    state = "locked" if assessment.is_locked else "unlocked"
    messages.success(request, f"Assessment {state}.")
    return redirect("assessments:list")


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def assessment_delete(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, institution=request.institution)
    if request.method == "POST":
        assessment.delete()
        messages.success(request, "Assessment deleted.")
        return redirect("assessments:list")
    return render(
        request,
        "assessments/confirm_delete.html",
        {"assessment": assessment},
    )


# ---------------------------------------------------------------------------
# Marks Entry
# ---------------------------------------------------------------------------
@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL, Role.CLASS_TEACHER, Role.SUBJECT_TEACHER)
def assessment_pick_class(request, pk):
    """Pick a class + subject before entering marks."""
    assessment = get_object_or_404(Assessment, pk=pk, institution=request.institution)
    targets = list(assessment.target_class_levels.all())
    streams = list(assessment.target_streams.all())
    subjects = Subject.objects.filter(institution=request.institution)
    return render(
        request,
        "assessments/pick_class.html",
        {
            "assessment": assessment,
            "targets": targets,
            "streams": streams,
            "subjects": subjects,
        },
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL, Role.CLASS_TEACHER, Role.SUBJECT_TEACHER)
def marks_entry(request, pk):
    """Enter / update marks for one (assessment, class[, stream], subject)."""
    assessment = get_object_or_404(Assessment, pk=pk, institution=request.institution)

    class_level_id = request.GET.get("class_level") or request.POST.get("class_level")
    stream_id = request.GET.get("stream") or request.POST.get("stream") or ""
    subject_id = request.GET.get("subject") or request.POST.get("subject")

    if not (class_level_id and subject_id):
        messages.error(request, "Pick a class and subject first.")
        return redirect("assessments:pick_class", pk=pk)

    subject = get_object_or_404(
        Subject, pk=subject_id, institution=request.institution
    )

    students_qs = Student.objects.filter(
        institution=request.institution, class_level_id=class_level_id
    )
    if stream_id:
        students_qs = students_qs.filter(stream_id=stream_id)
    students = list(students_qs.order_by("first_name", "second_name"))

    teacher = Teacher.objects.filter(
        institution=request.institution, user=request.user
    ).first()

    existing = {
        m.student_id: m
        for m in Mark.objects.filter(
            assessment=assessment, subject=subject, student__in=students
        )
    }

    if request.method == "POST":
        if assessment.is_locked:
            messages.error(request, "This assessment is locked. Marks cannot be edited.")
            return redirect("assessments:list")

        with transaction.atomic():
            saved = 0
            for student in students:
                raw = (request.POST.get(f"mark_{student.id}") or "").strip()
                if raw == "":
                    continue
                try:
                    val = Decimal(raw)
                except InvalidOperation:
                    continue
                if val < 0:
                    val = Decimal("0")
                if val > assessment.max_marks:
                    val = Decimal(assessment.max_marks)

                mark = existing.get(student.id) or Mark(
                    institution=request.institution,
                    assessment=assessment,
                    student=student,
                    subject=subject,
                )
                mark.marks = val
                if teacher:
                    mark.teacher = teacher
                mark.save()
                saved += 1

        messages.success(request, f"Saved {saved} marks for {subject.name}.")
        return redirect(
            f"{request.path}?class_level={class_level_id}&stream={stream_id}&subject={subject_id}"
        )

    rows = []
    for s in students:
        m = existing.get(s.id)
        rows.append(
            {
                "student": s,
                "marks": m.marks if m else "",
                "rubric": m.rubric_label if m else "",
                "points": m.points if m else "",
            }
        )

    return render(
        request,
        "assessments/marks_entry.html",
        {
            "assessment": assessment,
            "subject": subject,
            "rows": rows,
            "class_level_id": class_level_id,
            "stream_id": stream_id,
            "subject_id": subject_id,
        },
    )
