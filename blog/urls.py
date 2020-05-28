from django.conf.urls import url
from blog.views import BlogPostsView, BlogListView, BlogDetailView


urlpatterns = [
    url(r'^$', BlogPostsView.as_view(), name='blog_posts'),
    url(r'^(?P<cat_name>[\w\-]+)/$', BlogListView.as_view(), name="blog_index"),
    url(r'^/read/(?P<pk>\d+)/$', BlogDetailView.as_view(), name="blog_detail")
]
