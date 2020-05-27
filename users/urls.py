from django.conf.urls import url, include
from users.views import *


urlpatterns = [
    url(r'^(?P<pk>\d+)/$', ProfileUserView.as_view(), name='user'),
]
