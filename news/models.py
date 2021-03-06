from django.db import models
import uuid
from django.conf import settings
from django.contrib.postgres.indexes import BrinIndex
from pilkit.processors import ResizeToFill, ResizeToFit
from imagekit.models import ProcessedImageField
from users.helpers import upload_to_user_directory
from django.contrib.postgres.indexes import BrinIndex
from ckeditor_uploader.fields import RichTextUploadingField


class New(models.Model):

    id = models.BigIntegerField(unique=True, primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="uuid")
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(max_length=1000, verbose_name="Описание новости")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    image = ProcessedImageField(format='JPEG', options={'quality': 90}, upload_to=upload_to_user_directory, processors=[ResizeToFit(width=1024, upscale=False)])
    is_active = models.BooleanField(default=False, verbose_name='Пост активен')
    is_deleted = models.BooleanField(default=False, verbose_name='Пост удален')
    is_private = models.BooleanField(default=False, verbose_name='Пост приватный')
    content = RichTextUploadingField(config_name='default',external_plugin_resources=[('youtube','/static/ckeditor_plugins/youtube/youtube/','plugin.js',)],)

    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Время публикации")
    votes_off = models.BooleanField(default=False, verbose_name='Лайки-дизлайки отключены')

    def __str__(self):
        return self.title

    class Meta:
        indexes = (BrinIndex(fields=['created']),)
        verbose_name = "пост"
        verbose_name_plural = "посты"

    def all_visits_count(self):
        from stst.models import NewNumbers

        return NewNumbers.objects.filter(new=self.pk).values('pk').count()

    def likes(self):
        from common.model.votes import NewVotes
        likes = NewVotes.objects.filter(parent=self, vote__gt=0)
        return likes

    def dislikes(self):
        from common.model.votes import NewVotes
        dislikes = NewVotes.objects.filter(parent=self, vote__lt=0)
        return dislikes
