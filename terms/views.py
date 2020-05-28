from django.views.generic.base import TemplateView
from generic.mixins import CategoryListMixin


class TermsView(TemplateView, CategoryListMixin):
    template_name = "terms.html"
