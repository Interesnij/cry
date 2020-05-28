from django.views.generic.base import TemplateView
from generic.mixins import CategoryListMixin


class BlogCategoriesView(TemplateView, CategoryListMixin):
    template_name = "blog_categories.html"
