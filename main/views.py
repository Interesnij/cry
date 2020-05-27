from django.views.generic.base import TemplateView
from ad_categories.models import AdCategory
from skill_categories.models import SkillCategory


class MainPageView(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		from common.get_templates import get_template

		self.template_name = get_template(folder="main/", template="main.html", request=request)
		return super(MainPageView,self).get(request,*args,**kwargs)

	def get_context_data(self, **kwargs):
		from common.utils import last_ads_for_russia, last_courses_for_russia, last_ankets_for_russia

		context = super(MainPageView, self).get_context_data(**kwargs)
		context['ad_categories'] = AdCategory.objects.only("pk")
		context['last_ads'] = last_ads_for_russia()
		context['last_courses'] = last_courses_for_russia()
		context['last_ankets'] = last_ankets_for_russia()
		return context


class AdsPageView(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		from common.get_templates import get_ads_template

		self.template_name = get_ads_template(folder="main/ads/", template="ads.html", request=request)
		return super(AdsPageView,self).get(request,*args,**kwargs)

	def get_context_data(self, **kwargs):
		from common.utils import last_ads_for_russia

		context = super(AdsPageView, self).get_context_data(**kwargs)
		context['ad_categories'] = AdCategory.objects.only("pk")
		context['last_ads'] = last_ads_for_russia()
		return context


class CoursesPageView(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		from common.get_templates import get_skills_template

		self.template_name = get_skills_template(folder="main/courses/", template="courses.html", request=request)
		return super(CoursesPageView,self).get(request,*args,**kwargs)

	def get_context_data(self, **kwargs):
		from common.utils import last_courses_for_russia

		context = super(CoursesPageView, self).get_context_data(**kwargs)
		context['last_courses'] = last_courses_for_russia()
		context['skill_categories'] = SkillCategory.objects.only("pk")
		return context


class AnketsPageView(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		from common.get_templates import get_ankets_template

		self.template_name = get_ankets_template(folder="main/ankets/", template="ankets.html", request=request)
		return super(AnketsPageView,self).get(request,*args,**kwargs)

	def get_context_data(self, **kwargs):
		from common.utils import last_ankets_for_russia

		context = super(AnketsPageView, self).get_context_data(**kwargs)
		context['last_ankets'] = last_ankets_for_russia()
		return context


class MainPhoneSend(TemplateView):
	template_name="main/phone_verification.html"

	def get_context_data(self, **kwargs):
		context = super(MainPhoneSend, self).get_context_data(**kwargs)
		context['request_user'] = self.request.user
		return context
