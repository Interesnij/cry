from django.conf.urls import url
from blog_categories.views import BlogCategoriesView


urlpatterns = [
    url(r'^$', BlogCategoriesView.as_view(), name='blog_categories'),
]
