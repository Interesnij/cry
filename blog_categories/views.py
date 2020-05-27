from django.views.generic.base import TemplateView


class BlogCategoriesView(TemplateView):
    template_name = "blog_categories.html"
