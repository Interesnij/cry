from django.views.generic.base import ContextMixin
from django.conf import settings
from blog_categories.models import BlogCategory


class CategoryListMixin(ContextMixin):

	def get_context_data(self,**kwargs):
		context=super(CategoryListMixin,self).get_context_data(**kwargs)
		context["current_url"]=self.request.path
		context["blog_categories"]=BlogCategory.objects.all()
		return context
