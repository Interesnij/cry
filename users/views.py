from django.views.generic.base import TemplateView
from django.views.generic import ListView
from users.models import User
from generic.mixins import CategoryListMixin


class ProfileUserView(TemplateView, CategoryListMixin):
    template_name = None

    def get(self,request,*args,**kwargs):
        self.user=User.objects.get(pk=self.kwargs["pk"])
        self.template_name = self.user.get_template_user(folder="user/", template="user.html", request=request)
        return super(ProfileUserView,self).get(request,*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProfileUserView, self).get_context_data(**kwargs)
        context['user'] = self.user
        return context
