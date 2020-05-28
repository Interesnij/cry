from django.db import models
from django.conf import settings
from django.contrib.postgres.indexes import BrinIndex


class UserNumbers(models.Model):
    visitor = models.PositiveIntegerField(default=0, verbose_name="Кто заходит")
    target = models.PositiveIntegerField(default=0, verbose_name="К кому заходит")
    platform = models.PositiveIntegerField(default=0, verbose_name="0 Комп, 1 Телефон")
    created = models.DateField(auto_now_add=True, auto_now=False, verbose_name="Создано")

    class Meta:
        indexes = (BrinIndex(fields=['created']),)
        verbose_name="Кто к кому заходил"
        verbose_name_plural="Кто к кому заходил"


class BlogNumbers(models.Model):
    user = models.PositiveIntegerField(default=0, verbose_name="Кто заходит")
    blog = models.PositiveIntegerField(default=0, verbose_name="В какой пост заходил")
    platform = models.PositiveIntegerField(default=0, verbose_name="0 Комп, 1 Телефон")
    created = models.DateField(auto_now_add=True, auto_now=False, verbose_name="Создано")

    class Meta:
        indexes = (BrinIndex(fields=['created']),)
        #ordering = ['-created']
        verbose_name="Посещение постов"
        verbose_name_plural="Посещения постов"


class NewNumbers(models.Model):
    user = models.PositiveIntegerField(default=0, verbose_name="Кто смотрит")
    new = models.PositiveIntegerField(default=0, verbose_name="Какую новость смотрит")
    platform = models.PositiveIntegerField(default=0, verbose_name="0 Комп, 1 Телефон")
    created = models.DateField(auto_now_add=True, auto_now=False, verbose_name="Создано")

    class Meta:
        indexes = (BrinIndex(fields=['created']),)
        verbose_name="Посещение новости"
        verbose_name_plural="Посещения новости"
