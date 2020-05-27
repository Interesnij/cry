from django.conf.urls import url
from blog.views import BlogPostsView


urlpatterns = [
    url(r'^$', BlogPostsView.as_view(), name='blog_posts'),
]
