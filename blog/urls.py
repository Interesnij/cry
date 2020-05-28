from django.conf.urls import url
from blog.views import BlogPostsView, BlogListView


urlpatterns = [
    url(r'^$', BlogPostsView.as_view(), name='blog_posts'),
    url(r'^(?P<pk>\d+)/$', BlogListView.as_view(), name="blog_index")
]
