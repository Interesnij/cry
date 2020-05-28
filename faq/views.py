from django.views.generic.base import TemplateView
from generic.mixins import CategoryListMixin


class FAQView(TemplateView, CategoryListMixin):
    template_name = "faq.html"
