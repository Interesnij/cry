from django.conf.urls import url
from policy.views import PolicyView


urlpatterns = [
    url(r'^$', PolicyView.as_view(), name='policy'),
]
