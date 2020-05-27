from django.conf.urls import url
from skill_posts.views import BlogPostsView


urlpatterns = [
    url(r'^$', BlogPostsView.as_view(), name='blog_posts'),
]
