from django.conf.urls import url
from faq.views import FAQView


urlpatterns = [
    url(r'^$', FAQView.as_view(), name='faq'),
]
