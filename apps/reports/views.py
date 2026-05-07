"""Report card views."""
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.accounts.decorators import role_required
from apps.accounts.models import Role
from apps.assessments.models import Assessment
from apps.students.models import Student

from .services import render_student_report_pdf


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL, Role.CLASS_TEACHER, Role.SUBJECT_TEACHER, Role.STUDENT)
def reports_index(request):
    inst = request.institution
    assessments = (
        Assessment.objects.filter(institution=inst)
        .select_related("session")
        .order_by("-created_at")
    )
    if request.user.is_student:
        students = Student.objects.filter(institution=inst, user=request.user)
    else:
        students = Student.objects.filter(institution=inst).select_related(
            "class_level", "stream"
        )
    return render(
        request,
        "reports/index.html",
        {"assessments": assessments, "students": students},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL, Role.CLASS_TEACHER, Role.SUBJECT_TEACHER, Role.STUDENT)
def report_card_pdf(request, assessment_id, student_id):
    inst = request.institution
    assessment = get_object_or_404(Assessment, pk=assessment_id, institution=inst)
    student = get_object_or_404(Student, pk=student_id, institution=inst)

    # Students may only fetch their own report card.
    if request.user.is_student and student.user_id != request.user.id:
        raise Http404()

    pdf = render_student_report_pdf(student, assessment)
    safe_name = student.full_name.replace(" ", "_")
    filename = f"report_{safe_name}_{assessment.name.replace(' ', '_')}.pdf"
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response
