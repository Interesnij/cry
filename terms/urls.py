from django.conf.urls import url
from terms.views import TermsView


urlpatterns = [
    url(r'^$', TermsView.as_view(), name='terms'),
]
