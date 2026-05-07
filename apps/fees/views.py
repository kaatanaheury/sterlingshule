"""Fee views: structures, student liabilities, and payments."""
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import Role

from .forms import FeeStructureForm, PaymentForm, StudentFeeForm
from .models import FeeStructure, Payment, StudentFee


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def fees_overview(request):
    inst = request.institution
    rows = StudentFee.objects.filter(institution=inst).select_related(
        "student", "fee_structure", "fee_structure__session"
    )
    totals = rows.aggregate(req=Sum("required_amount"), paid=Sum("paid_amount"))
    structures = FeeStructure.objects.filter(institution=inst).select_related("session")
    return render(
        request,
        "fees/overview.html",
        {
            "rows": rows,
            "structures": structures,
            "total_required": totals["req"] or Decimal("0.00"),
            "total_paid": totals["paid"] or Decimal("0.00"),
            "total_balance": (totals["req"] or Decimal("0.00")) - (totals["paid"] or Decimal("0.00")),
        },
    )


# ----- Fee Structures -----
@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def structure_create(request):
    if request.method == "POST":
        form = FeeStructureForm(request.POST, institution=request.institution)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.save()
            form.save_m2m()
            messages.success(request, "Fee structure created.")
            return redirect("fees:overview")
    else:
        form = FeeStructureForm(institution=request.institution)
    return render(
        request,
        "fees/form_page.html",
        {"form": form, "title": "New fee structure", "back_url_name": "fees:overview"},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def structure_edit(request, pk):
    structure = get_object_or_404(FeeStructure, pk=pk, institution=request.institution)
    if request.method == "POST":
        form = FeeStructureForm(request.POST, instance=structure, institution=request.institution)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.save()
            form.save_m2m()
            messages.success(request, "Fee structure updated.")
            return redirect("fees:overview")
    else:
        form = FeeStructureForm(instance=structure, institution=request.institution)
    return render(
        request,
        "fees/form_page.html",
        {"form": form, "title": "Edit fee structure", "back_url_name": "fees:overview"},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def structure_apply(request, pk):
    """Auto-create StudentFee rows for every student in the targeted class levels."""
    structure = get_object_or_404(FeeStructure, pk=pk, institution=request.institution)
    from apps.students.models import Student

    targeted = structure.applies_to_class_levels.values_list("id", flat=True)
    students = Student.objects.filter(institution=request.institution, class_level_id__in=targeted)
    created = 0
    for s in students:
        _, was_created = StudentFee.objects.get_or_create(
            institution=request.institution,
            student=s,
            fee_structure=structure,
            defaults={"required_amount": structure.total_amount},
        )
        if was_created:
            created += 1
    messages.success(
        request,
        f"Applied '{structure.name}' to {students.count()} student(s) ({created} new liabilities).",
    )
    return redirect("fees:overview")


# ----- Student fees & payments -----
@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def student_fee_detail(request, pk):
    sf = get_object_or_404(
        StudentFee.objects.select_related("student", "fee_structure"),
        pk=pk,
        institution=request.institution,
    )
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.institution = request.institution
            payment.student_fee = sf
            payment.recorded_by = request.user
            payment.save()
            messages.success(request, f"Payment of {payment.amount} recorded.")
            return redirect("fees:student_fee", pk=sf.pk)
    else:
        form = PaymentForm()

    payments = sf.payments.all().order_by("-paid_at")
    return render(
        request,
        "fees/student_fee_detail.html",
        {"sf": sf, "form": form, "payments": payments},
    )


@login_required
@role_required(Role.ICT_ADMIN, Role.PRINCIPAL)
def student_fee_create(request):
    if request.method == "POST":
        form = StudentFeeForm(request.POST, institution=request.institution)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.institution = request.institution
            obj.save()
            messages.success(request, "Student fee added.")
            return redirect("fees:overview")
    else:
        form = StudentFeeForm(institution=request.institution)
    return render(
        request,
        "fees/form_page.html",
        {"form": form, "title": "Assign fee to student", "back_url_name": "fees:overview"},
    )
