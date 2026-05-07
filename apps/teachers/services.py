"""Helpers for creating Teacher accounts and importing them in bulk."""
from django.contrib.auth.hashers import make_password
from django.db import transaction

from apps.accounts.models import Role, User

from .models import Teacher
from apps.students.services import _read_rows  # reuse CSV/XLSX reader


def _unique_username(institution, base: str) -> str:
    base = (base or "teacher").strip().lower().replace(" ", "")
    candidate = base
    n = 1
    while User.objects.filter(institution=institution, username=candidate).exists():
        n += 1
        candidate = f"{base}{n}"
    return candidate


_TEACHER_ROLES = {"CLASS_TEACHER", "SUBJECT_TEACHER", "PRINCIPAL"}


@transaction.atomic
def create_teacher_with_user(
    *,
    institution,
    first_name: str,
    second_name: str,
    teacher_id: str,
    third_name: str = "",
    phone: str = "",
    email: str = "",
    role: str = Role.SUBJECT_TEACHER,
    initial_password: str | None = None,
    class_teacher_of_class=None,
    class_teacher_of_stream=None,
) -> Teacher:
    if role not in _TEACHER_ROLES:
        role = Role.SUBJECT_TEACHER

    username = _unique_username(institution, first_name)
    password = (initial_password or "").strip() or teacher_id or "teacher123"
    user = User.objects.create(
        username=username,
        password=make_password(password),
        role=role,
        institution=institution,
        first_name=first_name,
        last_name=second_name,
        email=email or "",
        must_change_password=True,
    )
    teacher = Teacher.objects.create(
        institution=institution,
        user=user,
        first_name=first_name,
        second_name=second_name,
        third_name=third_name or "",
        teacher_id=teacher_id,
        phone=phone or "",
        email=email or "",
        class_teacher_of_class=class_teacher_of_class,
        class_teacher_of_stream=class_teacher_of_stream,
    )
    return teacher


def import_teachers(*, institution, uploaded_file) -> dict:
    created = 0
    errors: list[str] = []

    for idx, raw in enumerate(_read_rows(uploaded_file), start=2):
        try:
            first_name = str(raw.get("first_name") or "").strip()
            second_name = str(raw.get("second_name") or "").strip()
            third_name = str(raw.get("third_name") or "").strip()
            tid = str(raw.get("teacher_id") or "").strip()
            phone = str(raw.get("phone") or "").strip()
            email = str(raw.get("email") or "").strip()
            role = str(raw.get("role") or "SUBJECT_TEACHER").strip().upper()

            if not (first_name and second_name and tid):
                errors.append(f"Row {idx}: missing first_name/second_name/teacher_id.")
                continue
            if Teacher.objects.filter(institution=institution, teacher_id=tid).exists():
                errors.append(f"Row {idx}: teacher_id '{tid}' already exists.")
                continue

            create_teacher_with_user(
                institution=institution,
                first_name=first_name,
                second_name=second_name,
                third_name=third_name,
                teacher_id=tid,
                phone=phone,
                email=email,
                role=role if role in _TEACHER_ROLES else Role.SUBJECT_TEACHER,
            )
            created += 1
        except Exception as exc:  # pragma: no cover
            errors.append(f"Row {idx}: {exc}")

    return {"created": created, "errors": errors}
