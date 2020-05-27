from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from django.utils.http import is_safe_url, urlunquote


class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        next = request.META.get('HTTP_REFERER')
        if next:
            next = urlunquote(next)
            if next != 'http://нытик.рус/login/':
                return next
            else:
                return '/profile'
