from django.utils import timezone
from django.db import models
from django.conf import settings
from pilkit.processors import ResizeToFill, ResizeToFit
from imagekit.models import ProcessedImageField
from ad_posts.helpers import upload_to_user_directory
from django.utils import timezone


class UserProfile(models.Model):
    id = models.BigIntegerField(primary_key=True, db_index=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="profile", verbose_name="Пользователь", on_delete=models.CASCADE)
    bio = models.TextField(max_length=1000, blank=True, verbose_name="Биография")
    сity = models.CharField(max_length=100, blank=True, verbose_name="Город")
    status = models.CharField(max_length=100, blank=True, verbose_name="статус-слоган")
    vk_url = models.URLField(blank=True, verbose_name="Ссылка на vk")
    youtube_url = models.URLField(blank=True, verbose_name="Ссылка на youtube")
    facebook_url = models.URLField(blank=True, verbose_name="Ссылка на facebook")
    instagram_url = models.URLField(blank=True, verbose_name="Ссылка на instagram")
    twitter_url = models.URLField(blank=True, verbose_name="Ссылка на twitter")
    avatar = ProcessedImageField(format='JPEG', options={'quality': 80}, upload_to=upload_to_user_directory, processors=[ResizeToFit(width=500, upscale=500)])

    def __str__(self):
        return self.user

    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
        index_together = [('id', 'user'),]


class OneUserLocation(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="user_location", verbose_name="Пользователь", on_delete=models.CASCADE)
    city_ru = models.CharField(max_length=100, blank=True, verbose_name="Город по-русски")
    city_en = models.CharField(max_length=100, blank=True, verbose_name="Город по-английски")
    city_lat = models.FloatField(blank=True, null=True, verbose_name="Ширина города")
    city_lon = models.FloatField(blank=True, null=True, verbose_name="Долгота города")
    region_ru = models.CharField(max_length=100, blank=True, verbose_name="Регион по-русски")
    region_en = models.CharField(max_length=100, blank=True, verbose_name="Регион по-английски")
    country_ru = models.CharField(max_length=100, blank=True, verbose_name="Страна по-русски")
    country_en = models.CharField(max_length=100, blank=True, verbose_name="Страна по-английски")
    phone = models.CharField(max_length=5, blank=True, verbose_name="Начало номера")

    class Meta:
        verbose_name="Местоположение 1"
        verbose_name_plural="Местоположения 1"
        index_together = [('id', 'user'),]

    def __str__(self):
        return '{}, {}, {}'.format(self.country_ru, self.region_ru, self.city_ru)

    def get_sity(self):
        return self.city_ru


class TwoUserLocation(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="user_location_2", verbose_name="Пользователь", on_delete=models.CASCADE)
    city_ru = models.CharField(max_length=100, blank=True, verbose_name="Город по-русски")
    city_en = models.CharField(max_length=100, blank=True, verbose_name="Город по-английски")
    city_lat = models.FloatField(blank=True, null=True, verbose_name="Ширина города")
    city_lon = models.FloatField(blank=True, null=True, verbose_name="Долгота города")
    region_ru = models.CharField(max_length=100, blank=True, verbose_name="Регион по-русски")
    region_en = models.CharField(max_length=100, blank=True, verbose_name="Регион по-английски")
    country_ru = models.CharField(max_length=100, blank=True, verbose_name="Страна по-русски")
    country_en = models.CharField(max_length=100, blank=True, verbose_name="Страна по-английски")
    phone = models.CharField(max_length=5, blank=True, verbose_name="Начало номера")

    class Meta:
        verbose_name="Местоположение 2"
        verbose_name_plural="Местоположения 2"
        index_together = [('id', 'user'),]

    def __str__(self):
        return '{}, {}, {}'.format(self.country_ru, self.region_ru, self.city_ru)


class ThreeUserLocation(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="user_location_3", verbose_name="Пользователь", on_delete=models.CASCADE)
    city_ru = models.CharField(max_length=100, blank=True, verbose_name="Город по-русски")
    city_en = models.CharField(max_length=100, blank=True, verbose_name="Город по-английски")
    city_lat = models.FloatField(blank=True, null=True, verbose_name="Ширина города")
    city_lon = models.FloatField(blank=True, null=True, verbose_name="Долгота города")
    region_ru = models.CharField(max_length=100, blank=True, verbose_name="Регион по-русски")
    region_en = models.CharField(max_length=100, blank=True, verbose_name="Регион по-английски")
    country_ru = models.CharField(max_length=100, blank=True, verbose_name="Страна по-русски")
    country_en = models.CharField(max_length=100, blank=True, verbose_name="Страна по-английски")
    phone = models.CharField(max_length=5, blank=True, verbose_name="Начало номера")

    class Meta:
        verbose_name="Местоположение 3"
        verbose_name_plural="Местоположения 3"
        index_together = [('id', 'user'),]

    def __str__(self):
        return '{}, {}, {}'.format(self.country_ru, self.region_ru, self.city_ru)


class IPUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="user_ip", verbose_name="Пользователь", on_delete=models.CASCADE)
    ip_1 = models.GenericIPAddressField(protocol='both', null=True, blank=True, verbose_name="ip 1")
    ip_2 = models.GenericIPAddressField(protocol='both', null=True, blank=True, verbose_name="ip 2")
    ip_3 = models.GenericIPAddressField(protocol='both', null=True, blank=True, verbose_name="ip 3")

    class Meta:
        verbose_name="ip пользователя"
        verbose_name_plural="ip пользователей"
        index_together = [('id', 'user'),]

    def __str__(self):
        return '{} - {}, {}, {}'.format(self.user.get_full_name(), self.ip_1, self.ip_2, self.ip_3)
