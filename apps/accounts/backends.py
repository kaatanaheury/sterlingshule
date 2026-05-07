"""Authentication backend that requires Institution Key + username + password."""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class InstitutionAuthBackend(ModelBackend):
    """
    Authenticate against Institution Key + username + password.

    - If `institution_key` is provided, the user MUST belong to the matching
      Institution.
    - If `institution_key` is omitted (e.g. Django admin login), behave like
      ModelBackend and only allow users with no institution (superusers).
    """

    def authenticate(self, request, username=None, password=None, institution_key=None, **kwargs):
        if username is None or password is None:
            return None

        User = get_user_model()
        try:
            if institution_key:
                user = User.objects.get(
                    username=username,
                    institution__institution_key=institution_key,
                    institution__is_active=True,
                )
            else:
                # Django admin / superuser path — only superusers without an
                # institution may sign in this way.
                user = User.objects.get(username=username, institution__isnull=True)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
