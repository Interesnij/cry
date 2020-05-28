from django.views.generic.base import TemplateView
from generic.mixins import CategoryListMixin


class PolicyView(TemplateView, CategoryListMixin):
    template_name = "policy.html"
