from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


User = get_user_model()


class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        login_value = (username or kwargs.get('email') or '').strip()
        if not login_value or not password:
            return None

        # Prefer an exact username match first. This keeps username login
        # deterministic even if a legacy account happens to share the same
        # value in another user's email field.
        username_user = User.objects.filter(username__iexact=login_value).first()
        if username_user and username_user.check_password(password) and self.user_can_authenticate(username_user):
            return username_user

        # New registrations enforce unique emails, but older/demo data may
        # predate that rule. Check every matching legacy record rather than
        # rejecting authentication simply because duplicate emails exist.
        for user in User.objects.filter(email__iexact=login_value):
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        return None
