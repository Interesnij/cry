from django.db import models
import uuid
from django.conf import settings
from django.contrib.postgres.indexes import BrinIndex
from pilkit.processors import ResizeToFill, ResizeToFit
from imagekit.models import ProcessedImageField
from users.helpers import upload_to_user_directory
from django.contrib.postgres.indexes import BrinIndex


class Blog(models.Model):

    id = models.BigIntegerField(unique=True, primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="uuid")
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(max_length=1000, verbose_name="Описание курса")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    category = models.ForeignKey('blog_categories.BlogCategory', on_delete=models.CASCADE, verbose_name="Категория")
    image = ProcessedImageField(format='JPEG', options={'quality': 90}, upload_to=upload_to_user_directory, processors=[ResizeToFit(width=1024, upscale=False)])
    video = models.CharField(max_length=200, null=True, blank=True, verbose_name="Ссылка на вводный видео-ролик")
    is_active = models.BooleanField(default=False, verbose_name='Курс активен')
    is_deleted = models.BooleanField(default=False, verbose_name='Курс удален')
    is_private = models.BooleanField(default=False, verbose_name='Курс приватный')

    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Время публикации")

    is_reklama = models.BooleanField(default=False, verbose_name='Это реклама')
    votes_off = models.BooleanField(default=False, verbose_name='Лайки-дизлайки отключены')

    def __str__(self):
        return self.title

    class Meta:
        indexes = (BrinIndex(fields=['created']),)
        verbose_name = "пост"
        verbose_name_plural = "посты"

    def all_visits_count(self):
        from stst.models import CourseNumbers

        return CourseNumbers.objects.filter(course=self.pk).values('pk').count()

    def likes(self):
        from common.model.votes import CourseVotes
        likes = CourseVotes.objects.filter(parent=self, vote__gt=0)
        return likes

    def dislikes(self):
        from common.model.votes import CourseVotes
        dislikes = CourseVotes.objects.filter(parent=self, vote__lt=0)
        return dislikes


class BlogFavourites(models.Model):
    course = models.ForeignKey(Blog, on_delete=models.CASCADE, verbose_name="Пост")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='blog_favorites', on_delete=models.CASCADE, verbose_name="Пользователь")
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Дата добавления")

    def __str__(self):
        return self.user

    class Meta:
        verbose_name = "Избранный Пост"
        verbose_name_plural = "Избранные Посты"
        unique_together = ('course', 'user',)
        indexes = (BrinIndex(fields=['created']),)
