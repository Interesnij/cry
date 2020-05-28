from django.views.generic.base import TemplateView
from generic.mixins import CategoryListMixin
from blog.models import Blog
from blog_categories.models import BlogCategory
from django.views.generic import ListView


class BlogPostsView(TemplateView, CategoryListMixin):
    template_name = "blog_posts.html"


class BlogListView(ListView, CategoryListMixin):
	model = Blog
	template_name = "blog_index.html"
	paginate_by = 20
	tag = ""

	def get(self,request,*args,**kwargs):
		if self.kwargs["pk"] == None:
			self.cat = BlogCategory.objects.first()
		else:
			self.cat = BlogCategory.objects.get(pk=self.kwargs["pk"])
		return super(BlogListView,self).get(request,*args,**kwargs)

	def get_queryset(self):
		blogs = self.cat.get_posts().order_by("-posted")
		if self.tag:
			blogs = Blog.objects.all()
			blogs = blogs.filter(tags__name=self.tag)
		return blogs

	def get_context_data(self,**kwargs):
		context = super(BlogListView,self).get_context_data(**kwargs)
		context["category"] = self.cat
		context["tag"] = self.tag
		return context
