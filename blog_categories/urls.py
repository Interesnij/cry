from django.conf.urls import url
from skill_categories.views import SkillCategoriesView


urlpatterns = [
    url(r'^$', SkillCategoriesView.as_view(), name='skill_categories'),
]
