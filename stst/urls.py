from django.conf.urls import url
from stst.views import StatView, StatBlogView


urlpatterns = [
    url(r'^$', StatView.as_view(), name='stat'),
    url(r'^blog/(?P<uuid>[0-9a-f-]+)/$', StatBlogView.as_view(), name='stat_blog'),
]
