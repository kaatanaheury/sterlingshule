"""Academics views: Sessions, Class Levels, Streams, Subjects, Departments."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import Role

from .forms import (
    ClassLevelForm,
    DepartmentForm,
    SessionForm,
    StreamForm,
    SubjectForm,
)
from .models import ClassLevel, Department, Session, Stream, Subject


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------
@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def academics_overview(request):
    inst = request.institution
    context = {
        "sessions": Session.objects.filter(institution=inst),
        "class_levels": ClassLevel.objects.filter(institution=inst),
        "streams": Stream.objects.filter(institution=inst).select_related("class_level"),
        "subjects": Subject.objects.filter(institution=inst),
        "departments": Department.objects.filter(institution=inst),
        "active_session": Session.active_for(inst),
    }
    return render(request, "academics/overview.html", context)


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------
@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def session_list(request):
    sessions = Session.objects.filter(institution=request.institution)
    return render(request, "academics/sessions_list.html", {"sessions": sessions})


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def session_create(request):
    return _session_form(request, instance=None)


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def session_edit(request, pk):
    session = get_object_or_404(Session, pk=pk, institution=request.institution)
    return _session_form(request, instance=session)


def _session_form(request, instance):
    if request.method == "POST":
        form = SessionForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.save()
            messages.success(request, "Session saved.")
            return redirect("academics:session_list")
    else:
        form = SessionForm(instance=instance)
    return render(
        request,
        "academics/_form_page.html",
        {
            "form": form,
            "title": "Edit session" if instance else "New session",
            "back_url_name": "academics:session_list",
        },
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def session_activate(request, pk):
    session = get_object_or_404(Session, pk=pk, institution=request.institution)
    session.is_active = True
    session.save()  # save() also deactivates other sessions
    messages.success(request, f"{session.name} is now the active session.")
    return redirect("academics:session_list")


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def session_delete(request, pk):
    session = get_object_or_404(Session, pk=pk, institution=request.institution)
    if request.method == "POST":
        session.delete()
        messages.success(request, "Session deleted.")
        return redirect("academics:session_list")
    return render(
        request,
        "academics/_confirm_delete.html",
        {"object": session, "label": "session", "back_url_name": "academics:session_list"},
    )


# ---------------------------------------------------------------------------
# Class Levels
# ---------------------------------------------------------------------------
@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def classlevel_list(request):
    rows = ClassLevel.objects.filter(institution=request.institution)
    return render(request, "academics/classlevels_list.html", {"class_levels": rows})


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def classlevel_create(request):
    return _classlevel_form(request, None)


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def classlevel_edit(request, pk):
    obj = get_object_or_404(ClassLevel, pk=pk, institution=request.institution)
    return _classlevel_form(request, obj)


def _classlevel_form(request, instance):
    if request.method == "POST":
        form = ClassLevelForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.save()
            messages.success(request, "Class level saved.")
            return redirect("academics:classlevel_list")
    else:
        form = ClassLevelForm(instance=instance)
    return render(
        request,
        "academics/_form_page.html",
        {
            "form": form,
            "title": "Edit class level" if instance else "New class level",
            "back_url_name": "academics:classlevel_list",
        },
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def classlevel_delete(request, pk):
    obj = get_object_or_404(ClassLevel, pk=pk, institution=request.institution)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Class level deleted.")
        return redirect("academics:classlevel_list")
    return render(
        request,
        "academics/_confirm_delete.html",
        {"object": obj, "label": "class level", "back_url_name": "academics:classlevel_list"},
    )


# ---------------------------------------------------------------------------
# Streams
# ---------------------------------------------------------------------------
@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def stream_list(request):
    rows = Stream.objects.filter(institution=request.institution).select_related(
        "class_level"
    )
    return render(request, "academics/streams_list.html", {"streams": rows})


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def stream_create(request):
    return _stream_form(request, None)


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def stream_edit(request, pk):
    obj = get_object_or_404(Stream, pk=pk, institution=request.institution)
    return _stream_form(request, obj)


def _stream_form(request, instance):
    if request.method == "POST":
        form = StreamForm(request.POST, instance=instance, institution=request.institution)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.save()
            messages.success(request, "Stream saved.")
            return redirect("academics:stream_list")
    else:
        form = StreamForm(instance=instance, institution=request.institution)
    return render(
        request,
        "academics/_form_page.html",
        {
            "form": form,
            "title": "Edit stream" if instance else "New stream",
            "back_url_name": "academics:stream_list",
        },
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def stream_delete(request, pk):
    obj = get_object_or_404(Stream, pk=pk, institution=request.institution)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Stream deleted.")
        return redirect("academics:stream_list")
    return render(
        request,
        "academics/_confirm_delete.html",
        {"object": obj, "label": "stream", "back_url_name": "academics:stream_list"},
    )


# ---------------------------------------------------------------------------
# Subjects
# ---------------------------------------------------------------------------
@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def subject_list(request):
    rows = Subject.objects.filter(institution=request.institution)
    return render(request, "academics/subjects_list.html", {"subjects": rows})


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def subject_create(request):
    return _subject_form(request, None)


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def subject_edit(request, pk):
    obj = get_object_or_404(Subject, pk=pk, institution=request.institution)
    return _subject_form(request, obj)


def _subject_form(request, instance):
    if request.method == "POST":
        form = SubjectForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.save()
            messages.success(request, "Subject saved.")
            return redirect("academics:subject_list")
    else:
        form = SubjectForm(instance=instance)
    return render(
        request,
        "academics/_form_page.html",
        {
            "form": form,
            "title": "Edit subject" if instance else "New subject",
            "back_url_name": "academics:subject_list",
        },
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def subject_delete(request, pk):
    obj = get_object_or_404(Subject, pk=pk, institution=request.institution)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Subject deleted.")
        return redirect("academics:subject_list")
    return render(
        request,
        "academics/_confirm_delete.html",
        {"object": obj, "label": "subject", "back_url_name": "academics:subject_list"},
    )


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------
@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def department_list(request):
    rows = Department.objects.filter(institution=request.institution).select_related("head")
    return render(request, "academics/departments_list.html", {"departments": rows})


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def department_create(request):
    return _department_form(request, None)


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def department_edit(request, pk):
    obj = get_object_or_404(Department, pk=pk, institution=request.institution)
    return _department_form(request, obj)


def _department_form(request, instance):
    if request.method == "POST":
        form = DepartmentForm(
            request.POST, instance=instance, institution=request.institution
        )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.save()
            form.save_m2m()
            messages.success(request, "Department saved.")
            return redirect("academics:department_list")
    else:
        form = DepartmentForm(instance=instance, institution=request.institution)
    return render(
        request,
        "academics/_form_page.html",
        {
            "form": form,
            "title": "Edit department" if instance else "New department",
            "back_url_name": "academics:department_list",
        },
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def department_delete(request, pk):
    obj = get_object_or_404(Department, pk=pk, institution=request.institution)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Department deleted.")
        return redirect("academics:department_list")
    return render(
        request,
        "academics/_confirm_delete.html",
        {"object": obj, "label": "department", "back_url_name": "academics:department_list"},
    )
