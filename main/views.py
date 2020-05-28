from django.views.generic.base import TemplateView
from blog_categories.models import BlogCategory
from generic.mixins import CategoryListMixin


class MainPageView(TemplateView, CategoryListMixin):
	template_name = None

	def get(self,request,*args,**kwargs):
		from common.get_templates import get_template

		self.template_name = get_template(folder="main/", template="main.html", request=request)
		return super(MainPageView,self).get(request,*args,**kwargs)

	def get_context_data(self, **kwargs):
		context = super(MainPageView, self).get_context_data(**kwargs)
		context['blog_categories'] = BlogCategory.objects.only("pk")
		return context
