"""
When a new Institution is created:
  1. Auto-create an ICT Admin user with a temporary password.
  2. Seed Grades 1..6.
  3. Seed default subjects: Mathematics, English, Kiswahili, Science, Social Studies.
"""
import secrets
import string

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Institution


def _temp_password(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@receiver(post_save, sender=Institution)
def bootstrap_new_institution(sender, instance: Institution, created: bool, **kwargs):
    if not created:
        return

    # Lazy imports to avoid circular dependencies.
    from apps.accounts.models import User, Role
    from apps.academics.models import ClassLevel, Subject

    # 1) Create ICT Admin
    base_username = f"ictadmin_{instance.institution_key}"
    username = base_username
    suffix = 1
    while User.objects.filter(username=username).exists():
        suffix += 1
        username = f"{base_username}_{suffix}"

    temp_password = _temp_password(10)
    ict_admin = User.objects.create_user(
        username=username,
        password=temp_password,
        role=Role.ICT_ADMIN,
        institution=instance,
        first_name="ICT",
        last_name="Admin",
    )
    ict_admin.must_change_password = True
    ict_admin.save(update_fields=["must_change_password"])

    # Stash temp credentials so the global admin can read them once.
    # They are persisted on a one-off model so the password is never lost.
    from .models_extras import InstitutionBootstrapCredentials
    InstitutionBootstrapCredentials.objects.create(
        institution=instance,
        username=username,
        temporary_password=temp_password,
    )

    # 2) Seed Grades 1..6
    for i in range(1, 7):
        ClassLevel.objects.create(
            institution=instance,
            name=f"Grade {i}",
            order=i,
        )

    # 3) Seed default subjects
    for code, name in [
        ("MATH", "Mathematics"),
        ("ENG", "English"),
        ("KIS", "Kiswahili"),
        ("SCI", "Science"),
        ("SST", "Social Studies"),
    ]:
        Subject.objects.create(
            institution=instance,
            name=name,
            code=code,
        )
