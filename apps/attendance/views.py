"""Attendance views: pick class+date, mark all present by default, save."""
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from apps.academics.models import ClassLevel, Stream
from apps.accounts.decorators import role_required
from apps.accounts.models import Role
from apps.students.models import Student

from .models import AttendanceDay, AttendanceStatus, StudentAttendance


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL, Role.CLASS_TEACHER, Role.SUBJECT_TEACHER)
def attendance_overview(request):
    inst = request.institution
    today = date.today()
    days = (
        AttendanceDay.objects.filter(institution=inst)
        .select_related("class_level", "stream")
        .order_by("-date")[:30]
    )
    return render(
        request,
        "attendance/overview.html",
        {
            "days": days,
            "today": today,
            "class_levels": ClassLevel.objects.filter(institution=inst),
            "streams": Stream.objects.filter(institution=inst).select_related("class_level"),
        },
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL, Role.CLASS_TEACHER, Role.SUBJECT_TEACHER)
def mark_attendance(request):
    """GET → render form. POST → upsert AttendanceDay + entries."""
    inst = request.institution

    src = request.POST if request.method == "POST" else request.GET
    class_level_id = src.get("class_level")
    stream_id = src.get("stream") or ""
    date_str = src.get("date") or date.today().isoformat()

    if not class_level_id:
        messages.error(request, "Pick a class first.")
        return redirect("attendance:overview")

    students_qs = Student.objects.filter(
        institution=inst, class_level_id=class_level_id
    )
    if stream_id:
        students_qs = students_qs.filter(stream_id=stream_id)
    students = list(students_qs.order_by("first_name", "second_name"))

    day, _ = AttendanceDay.objects.get_or_create(
        institution=inst,
        date=date_str,
        class_level_id=class_level_id,
        stream_id=stream_id or None,
        defaults={"recorded_by": request.user},
    )
    existing = {e.student_id: e for e in day.entries.all()}

    if request.method == "POST" and src.get("save"):
        with transaction.atomic():
            for s in students:
                status = src.get(f"status_{s.id}", AttendanceStatus.PRESENT)
                reason = src.get(f"reason_{s.id}", "").strip()
                entry = existing.get(s.id) or StudentAttendance(
                    institution=inst, attendance_day=day, student=s
                )
                entry.status = status if status in dict(AttendanceStatus.choices) else AttendanceStatus.PRESENT
                entry.reason = reason if entry.status != AttendanceStatus.PRESENT else ""
                entry.save()
            day.recorded_by = request.user
            day.save(update_fields=["recorded_by", "updated_at"])
        messages.success(request, "Attendance saved.")
        return redirect(
            f"{request.path}?class_level={class_level_id}&stream={stream_id}&date={date_str}"
        )

    rows = []
    for s in students:
        e = existing.get(s.id)
        rows.append(
            {
                "student": s,
                "status": e.status if e else AttendanceStatus.PRESENT,
                "reason": e.reason if e else "",
            }
        )

    return render(
        request,
        "attendance/mark.html",
        {
            "day": day,
            "rows": rows,
            "class_level_id": class_level_id,
            "stream_id": stream_id,
            "date": date_str,
            "statuses": AttendanceStatus.choices,
        },
    )
