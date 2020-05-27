from django.views.generic.base import TemplateView


class TermsView(TemplateView):
    template_name = "terms.html"
