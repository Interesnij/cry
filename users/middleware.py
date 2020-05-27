from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from users.models import User
from django.conf import settings
import datetime

class UpdateLastActivityMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user'), 'UpdateLastActivityMiddleware требует установки промежуточного программного обеспечения аутентификации.'
        now = datetime.datetime.now()

        User.objects.filter(id=request.user.id) \
                    .update(last_activity=now)
