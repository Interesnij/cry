from django.views.generic.base import TemplateView
from generic.mixins import CategoryListMixin
from django.views.generic import ListView
from news.models import New


class NewsListView(ListView):
    template_name = None
    model = New
    paginate_by = 30

    def get(self,request,*args,**kwargs):
        from common.get_templates import get_template

        self.template_name = get_template(folder="news/", template="page.html", request=request)
        return super(NewsListView,self).get(request,*args,**kwargs)

    def get_queryset(self):
        news = New.objects.only("pk")
        return news


class NewsDetailView(TemplateView):
    template_name = None

    def get(self,request,*args,**kwargs):
        from common.get_templates import get_template

        self.new = New.objects.get(pk=self.kwargs["pk"])
        self.template_name = get_template(folder="news/", template="detail.html", request=request)
        return super(NewsDetailView,self).get(request,*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(NewsDetailView, self).get_context_data(**kwargs)
        context['new'] = self.new
        return context
