"""Analytics: top students, rubric distribution, attendance summary."""
from collections import Counter, defaultdict
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.accounts.decorators import role_required
from apps.accounts.models import Role
from apps.assessments.models import Assessment, Mark
from apps.attendance.models import AttendanceStatus, StudentAttendance
from apps.fees.models import StudentFee


def _build_analytics(institution, assessment_id=None):
    inst = institution
    assessments = Assessment.objects.filter(institution=inst).order_by("-created_at")
    selected = None
    if assessment_id:
        selected = assessments.filter(pk=assessment_id).first()
    elif assessments.exists():
        selected = assessments.first()

    # ----- Top students by total marks for the selected assessment -----
    top_students = []
    rubric_counts = Counter()
    subject_avg = []
    if selected:
        marks_qs = (
            Mark.objects.filter(assessment=selected)
            .select_related("student", "student__class_level", "subject")
        )
        per_student_total = defaultdict(lambda: [0, 0, None])  # total_marks, total_points, student
        for m in marks_qs:
            slot = per_student_total[m.student_id]
            slot[0] += float(m.marks)
            slot[1] += int(m.points)
            slot[2] = m.student
            rubric_counts[m.rubric_label or "—"] += 1

        ranked = sorted(per_student_total.values(), key=lambda x: x[0], reverse=True)[:10]
        top_students = [
            {"student": row[2], "total_marks": row[0], "total_points": row[1]}
            for row in ranked
        ]

        subject_avg_qs = (
            marks_qs.values("subject__name")
            .annotate(avg=Avg("marks"), count=Count("id"))
            .order_by("subject__name")
        )
        subject_avg = list(subject_avg_qs)

    # ----- Attendance summary (this institution, all-time top-level) -----
    att_counts = (
        StudentAttendance.objects.filter(institution=inst)
        .values("status")
        .annotate(n=Count("id"))
    )
    attendance_summary = {row["status"]: row["n"] for row in att_counts}

    # ----- Fees -----
    fees = StudentFee.objects.filter(institution=inst).aggregate(
        req=Sum("required_amount"), paid=Sum("paid_amount")
    )
    fees_required = float(fees["req"] or 0)
    fees_paid = float(fees["paid"] or 0)

    att_label = dict(AttendanceStatus.choices)
    attendance_rows = [
        {"code": code, "label": label, "count": attendance_summary.get(code, 0)}
        for code, label in att_label.items()
    ]
    return {
        "assessments": assessments,
        "selected": selected,
        "top_students": top_students,
        "rubric_counts": dict(rubric_counts),
        "subject_avg": subject_avg,
        "attendance_rows": attendance_rows,
        "fees_required": fees_required,
        "fees_paid": fees_paid,
        "fees_balance": fees_required - fees_paid,
    }


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL, Role.CLASS_TEACHER)
def analytics_index(request):
    assessment_id = request.GET.get("assessment")
    ctx = _build_analytics(request.institution, assessment_id=assessment_id)
    return render(request, "analytics/index.html", ctx)


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL, Role.CLASS_TEACHER)
def analytics_pdf(request):
    """Export the analytics dashboard as a PDF."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    inst = request.institution
    ctx = _build_analytics(inst, assessment_id=request.GET.get("assessment"))

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=f"{inst.name} — Analytics")
    base = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=base["Heading1"], textColor=colors.HexColor("#006400"), fontSize=18, alignment=1)
    h2 = ParagraphStyle("h2", parent=base["Heading2"], textColor=colors.HexColor("#008000"), fontSize=12)
    normal = base["Normal"]

    story = [Paragraph(inst.name, h1), Paragraph("Analytics report", h2), Spacer(1, 0.3 * cm)]
    if ctx["selected"]:
        story.append(Paragraph(f"Assessment: <b>{ctx['selected'].name}</b> · {ctx['selected'].session.name}", normal))
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("Top 10 students", h2))
        data = [["Rank", "Name", "Class", "Total marks", "Total points"]]
        for i, t in enumerate(ctx["top_students"], start=1):
            data.append([
                str(i),
                t["student"].full_name,
                t["student"].class_level.name,
                f"{t['total_marks']:.1f}",
                str(t["total_points"]),
            ])
        if len(data) == 1:
            data.append(["—", "No marks recorded", "—", "—", "—"])
        tbl = Table(data, colWidths=[1.5 * cm, 6 * cm, 3 * cm, 3 * cm, 3 * cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#006400")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#006400")),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("Rubric distribution", h2))
        rd = [["Rubric", "Count"]] + [[k, str(v)] for k, v in sorted(ctx["rubric_counts"].items())]
        if len(rd) == 1:
            rd.append(["—", "0"])
        tbl2 = Table(rd, colWidths=[6 * cm, 4 * cm])
        tbl2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#008000")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOX", (0, 0), (-1, -1), 0.4, colors.lightgrey),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        story.append(tbl2)
        story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Fees overview", h2))
    fees_tbl = Table(
        [["Required", "Paid", "Balance"], [f"{ctx['fees_required']:.2f}", f"{ctx['fees_paid']:.2f}", f"{ctx['fees_balance']:.2f}"]],
        colWidths=[5 * cm, 5 * cm, 5 * cm],
    )
    fees_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#006400")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ]))
    story.append(fees_tbl)

    doc.build(story)
    response = HttpResponse(buf.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="analytics.pdf"'
    return response
