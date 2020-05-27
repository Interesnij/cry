from django.views.generic.base import TemplateView
from blog_categories.models import BlogCategory
from django.http import HttpResponse


class BlogPostsView(TemplateView):
    template_name = "blog_posts.html"
