from django.conf.urls import url, include
from main.views import MainPageView, AdsPageView, CoursesPageView, AnketsPageView, MainPhoneSend


urlpatterns = [
	url(r'^$', MainPageView.as_view(), name="main"),
	url(r'ads/$', AdsPageView.as_view(), name="ads_main"),
	url(r'courses/$', CoursesPageView.as_view(), name="courses_main"),
	url(r'ankets/$', AnketsPageView.as_view(), name="ankets_main"),

	url(r'^phone_send/$', MainPhoneSend.as_view(), name="phone_sendd"),
]
