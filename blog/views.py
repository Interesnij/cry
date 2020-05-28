from django.views.generic.base import TemplateView
from generic.mixins import CategoryListMixin
from blog.models import Blog
from blog_categories.models import BlogCategory
from django.views.generic import ListView


class BlogPostsView(TemplateView, CategoryListMixin):
    template_name = "blog_posts.html"


class BlogListView(ListView, CategoryListMixin):
	model = Blog
	template_name = None
	paginate_by = 20
	tag = ""

	def get(self,request,*args,**kwargs):
        from common.get_templates import get_template
        
		if self.kwargs["cat_name"] == None:
			self.cat = BlogCategory.objects.first()
		else:
			self.cat = BlogCategory.objects.get(name_en=self.kwargs["cat_name"])
        self.template_name = get_template(folder="blog/", template="page.html", request=request)
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


class BlogDetailView(TemplateView):
    template_name = None

    def get(self,request,*args,**kwargs):
        from common.get_templates import get_template

        self.blog = Blog.objects.get(pk=self.kwargs["pk"])
        self.template_name = get_template(folder="blog/", template="detail.html", request=request)
        return super(NewsDetailView,self).get(request,*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(NewsDetailView, self).get_context_data(**kwargs)
        context['blog'] = self.blog
        return context
