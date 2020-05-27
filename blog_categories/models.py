from django.db import models
from django.db.models import Q


class BlogCategory(models.Model):
	name_ru = models.CharField(max_length=100, unique=True, verbose_name="Русское название")
	name_en = models.CharField(max_length=100, unique=True, verbose_name="Английское название")
	order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядковый номер")
	image = models.ImageField(blank=True, verbose_name="Изображение", upload_to="blog_category/cat")

	def __str__(self):
		return self.name_ru

	class Meta:
		verbose_name = "Категория"
		verbose_name_plural = "Категории"
		ordering = ['order']

	def get_course(self):
		ads_query = Q(category__category__id=self.id, creator__is_blocked=False, is_deleted=False, is_active=True)
		ads = Course.objects.filter(ads_query)
		return ads
