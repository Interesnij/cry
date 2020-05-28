from django.conf.urls import url
from news.views import NewsListView, NewsDetailView


urlpatterns = [
    url(r'^$', NewsListView.as_view(), name='news_index'),
    url(r'^(?P<pk>\d+)/$', NewsDetailView.as_view(), name="news_detail")
]
