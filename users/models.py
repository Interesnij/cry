import uuid
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from django.db import models
from rest_framework.exceptions import ValidationError, PermissionDenied


class User(AbstractUser):
    is_email_verified = models.BooleanField(default=False, verbose_name='Почта подтверждена')
    is_phone_verified = models.BooleanField(default=False, verbose_name='Телефон подтвержден')
    is_deleted = models.BooleanField(verbose_name="Удален", default=False, )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="uuid")
    last_activity= models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name='Активность')
    phone = models.CharField(max_length=17, unique=True, blank=True, verbose_name='Телефон')
    is_deleted = models.BooleanField(default=False, verbose_name='Пользователь удален')
    is_blocked = models.BooleanField(default=False, verbose_name='Пользователь заблокирован')
    USERNAME_FIELD = 'phone'

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def get_full_name(self):
        return  str(self.first_name) + " " + str(self.last_name)

    def get_users_count(self):
        return User.objects.all().values("pk").count()

    def __str__(self):
        return  self.get_full_name()

    def get_online(self):
        from datetime import datetime, timedelta

        now = datetime.now()
        onl = self.last_activity + timedelta(minutes=3)
        if now < onl:
            return True
        else:
            return False

    def get_template_user(self, folder, template, request):
        import re
        from stst.models import UserNumbers

        if self.pk == request.user.pk:
            if not request.user.is_phone_verified:
                template_name = "main/phone_verification.html"
            else:
                template_name = folder + "my_" + template
        elif request.user.pk != self.pk and request.user.is_authenticated:
            if not request.user.is_phone_verified:
                template_name = "main/phone_verification.html"
            elif request.user.is_blocked:
                template_name = "generic/you_are_block.html"
            elif request.user.is_blocked_with_user_with_id(user_id=self.pk):
                template_name = folder + "block_" + template
            elif request.user.is_deleted:
                template_name = "generic/deleted_page.html"
            else:
                template_name = folder + template
        elif request.user.is_anonymous:
            template_name = folder + "anon_" + template

        MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)
        if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
            template_name = "mob_" + template_name
            if request.user.is_authenticated:
                UserNumbers.objects.create(visitor=request.user.pk, target=self.pk, platform=1)
        else:
            if request.user.is_authenticated:
                UserNumbers.objects.create(visitor=request.user.pk, target=self.pk, platform=0)
        return template_name

    def get_my_template(self, folder, template, request):
        import re
        if self.pk == request.user.pk:
            if not request.user.is_phone_verified:
                template_name = "main/phone_verification.html"
            elif request.user.is_deleted:
                template_name = "generic/deleted_page.html"
            elif request.user.is_blocked:
                template_name = "generic/blocked_page.html"
            elif request.user.is_anonymous:
                template_name = "main/anon_page.html"
            else:
                template_name = folder + template
        MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)
        if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
            template_name = "mob_" + template_name
        return template_name

    def is_adding_user_with_id(self, user_id):
        return self.adding_user.filter(added_user__id=user_id).exists()

    def is_added_user_with_id(self, user_id):
        return self.added_user.filter(adding_user__id=user_id).exists()

    def is_ad_in_favorite(self, ad_id):
        return self.ad_favorites.filter(ad__id=ad_id).exists()

    def is_ad_visited(self, ad_id):
        from stst.models import AdNumbers
        return AdNumbers.objects.filter(user=self.pk, ad=ad_id).exists()

    def is_course_visited(self, course_id):
        from stst.models import CourseNumbers
        return CourseNumbers.objects.filter(user=self.pk, course=course_id).exists()

    def is_anketa_visited(self, anketa_id):
        from stst.models import AnketaNumbers
        return AnketaNumbers.objects.filter(user=self.pk, anketa=anketa_id).exists()

    def is_course_in_favorite(self, course_id):
        return self.course_favorites.filter(course__id=course_id).exists()

    def is_anketa_in_favorite(self, anketa_id):
        return self.anketa_favorites.filter(anketa__id=anketa_id).exists()

    def is_blocked_with_user_with_id(self, user_id):
        from users.model.list import UserBlock
        return UserBlock.users_are_blocked(user_a_id=self.pk, user_b_id=user_id)

    def is_user_blocked(self, user_id):
        from users.model.list import UserBlock
        return UserBlock.users_are_blocked(user_a_id=user_id, user_b_id=self.pk)

    def is_administrator(self):
        from users.model.profile import UserStaff
        return UserStaff.objects.filter(user__id=self.pk, is_administrator=True).exists()
    def is_moderator(self):
        from users.model.profile import UserStaff
        return UserStaff.objects.filter(user__id=self.pk, is_moderator=True).exists()
    def is_editor(self):
        from users.model.profile import UserStaff
        return UserStaff.objects.filter(user__id=self.pk, is_editor=True).exists()
    def is_advertiser(self):
        from users.model.profile import UserStaff
        return UserStaff.objects.filter(user__id=self.pk, is_advertiser=True).exists()
    def is_staff_user(self):
        if self.is_administrator() or self.is_editor() or self.is_moderator():
            return True
        else:
            return False

    def is_ad_administrator(self):
        from users.model.profile import UserAdStaff
        return UserAdStaff.objects.filter(user__id=self.pk, is_administrator=True).exists()
    def is_ad_moderator(self):
        from users.model.profile import UserAdStaff
        return UserAdStaff.objects.filter(user__id=self.pk, is_moderator=True).exists()
    def is_ad_editor(self):
        from users.model.profile import UserAdStaff
        return UserAdStaff.objects.filter(user__id=self.pk, is_editor=True).exists()
    def is_ad_advertiser(self):
        from users.model.profile import UserAdStaff
        return UserAdStaff.objects.filter(user__id=self.pk, is_advertiser=True).exists()
    def is_ad_staff(self):
        if self.is_ad_administrator() or self.is_ad_editor() or self.is_ad_moderator():
            return True
        else:
            return False

    def is_anketa_administrator(self):
        from users.model.profile import UserAnketaStaff
        return UserAnketaStaff.objects.filter(user__id=self.pk, is_administrator=True).exists()
    def is_anketa_moderator(self):
        from users.model.profile import UserAnketaStaff
        return UserAnketaStaff.objects.filter(user__id=self.pk, is_moderator=True).exists()
    def is_anketa_editor(self):
        from users.model.profile import UserAnketaStaff
        return UserAnketaStaff.objects.filter(user__id=self.pk, is_editor=True).exists()
    def is_anketa_advertiser(self):
        from users.model.profile import UserAnketaStaff
        return UserAnketaStaff.objects.filter(user__id=self.pk, is_advertiser=True).exists()
    def is_anketa_staff(self):
        if self.is_anketa_administrator() or self.is_anketa_editor() or self.is_anketa_moderator():
            return True
        else:
            return False

    def is_skill_administrator(self):
        from users.model.profile import UserSkillStaff
        return UserSkillStaff.objects.filter(user__id=self.pk, is_administrator=True).exists()
    def is_skill_teacher(self):
        from users.model.profile import UserSkillStaff
        return UserSkillStaff.objects.filter(user__id=self.pk, is_teacher=True).exists()
    def is_skill_moderator(self):
        from users.model.profile import UserSkillStaff
        return UserSkillStaff.objects.filter(user__id=self.pk, is_moderator=True).exists()
    def is_skill_editor(self):
        from users.model.profile import UserSkillStaff
        return UserSkillStaff.objects.filter(user__id=self.pk, is_editor=True).exists()
    def is_skill_advertiser(self):
        from users.model.profile import UserSkillStaff
        return UserSkillStaff.objects.filter(user__id=self.pk, is_advertiser=True).exists()
    def is_skill_staff(self):
        if self.is_skill_administrator() or self.is_skill_editor() or self.is_skill_moderator():
            return True
        else:
            return False

    def is_can_work_ad_administrator(self):
        from users.model.profile import CanAddStaffAdUser
        return CanAddStaffAdUser.objects.filter(user__id=self.pk, can_work_administrator=True).exists()
    def is_can_work_ad_moderator(self):
        from users.model.profile import CanAddStaffAdUser
        return CanAddStaffAdUser.objects.filter(user__id=self.pk, can_work_moderator=True).exists()
    def is_can_work_ad_editor(self):
        from users.model.profile import CanAddStaffAdUser
        return CanAddStaffAdUser.objects.filter(user__id=self.pk, can_work_editor=True).exists()
    def is_can_work_ad_advertiser(self):
        from users.model.profile import CanAddStaffAdUser
        return CanAddStaffAdUser.objects.filter(user__id=self.pk, can_work_advertiser=True).exists()
    def is_ad_staff_worker(self):
        if self.is_can_work_ad_administrator() or self.is_can_work_ad_editor() or self.is_can_work_ad_advertiser() or self.is_can_work_ad_moderator():
            return True
        else:
            return False

    def is_can_work_skill_administrator(self):
        from users.model.profile import CanAddStaffSkillUser
        return CanAddStaffSkillUser.objects.filter(user__id=self.pk, can_work_administrator=True).exists()
    def is_can_work_skill_moderator(self):
        from users.model.profile import CanAddStaffSkillUser
        return CanAddStaffSkillUser.objects.filter(user__id=self.pk, can_work_moderator=True).exists()
    def is_can_work_skill_editor(self):
        from users.model.profile import CanAddStaffSkillUser
        return CanAddStaffSkillUser.objects.filter(user__id=self.pk, can_work_editor=True).exists()
    def is_can_work_skill_advertiser(self):
        from users.model.profile import CanAddStaffSkillUser
        return CanAddStaffSkillUser.objects.filter(user__id=self.pk, can_work_advertiser=True).exists()
    def is_can_work_skill_teacher(self):
        from users.model.profile import CanAddStaffSkillUser
        return CanAddStaffSkillUser.objects.filter(user__id=self.pk, can_work_teacher=True).exists()
    def is_skill_staff_worker(self):
        if self.is_can_work_skill_administrator() or self.is_can_work_skill_editor() or self.is_can_work_skill_advertiser() or self.is_can_work_skill_moderator() or self.is_can_work_skill_teacher():
            return True
        else:
            return False

    def is_can_work_anketa_administrator(self):
        from users.model.profile import CanAddStaffAnketaUser
        return CanAddStaffAnketaUser.objects.filter(user__id=self.pk, can_work_administrator=True).exists()
    def is_can_work_anketa_moderator(self):
        from users.model.profile import CanAddStaffAnketaUser
        return CanAddStaffAnketaUser.objects.filter(user__id=self.pk, can_work_moderator=True).exists()
    def is_can_work_anketa_editor(self):
        from users.model.profile import CanAddStaffAnketaUser
        return CanAddStaffAnketaUser.objects.filter(user__id=self.pk, can_work_editor=True).exists()
    def is_can_work_anketa_advertiser(self):
        from users.model.profile import CanAddStaffAnketaUser
        return CanAddStaffAnketaUser.objects.filter(user__id=self.pk, can_work_advertiser=True).exists()
    def is_anketa_staff_worker(self):
        if self.is_can_work_anketa_administrator() or self.is_can_work_anketa_editor() or self.is_can_work_anketa_advertiser() or self.is_can_work_anketa_moderator():
            return True
        else:
            return False

    def is_can_work_administrator(self):
        from users.model.profile import CanAddStaffUser
        return CanAddStaffUser.objects.filter(user__id=self.pk, can_work_administrator=True).exists()
    def is_can_work_moderator(self):
        from users.model.profile import CanAddStaffUser
        return CanAddStaffUser.objects.filter(user__id=self.pk, can_work_moderator=True).exists()
    def is_can_work_editor(self):
        from users.model.profile import CanAddStaffUser
        return CanAddStaffUser.objects.filter(user__id=self.pk, can_work_editor=True).exists()
    def is_can_work_advertiser(self):
        from users.model.profile import CanAddStaffUser
        return CanAddStaffUser.objects.filter(user__id=self.pk, can_work_advertiser=True).exists()
    def is_staff_worker(self):
        if self.is_can_work_administrator() or self.is_can_work_editor() or self.is_can_work_advertiser() or self.is_can_work_moderator():
            return True
        else:
            return False

    def has_blocked_user_with_id(self, user_id):
        return self.user_blocks.filter(blocked_user_id=user_id).exists()

    def unsubscribe_user(self, user):
        return self.unsubscribe_user_with_id(user.pk)

    def unsubscribe_user_with_id(self, user_id):
        from users.model.list import Subscribe
        subscribe = Subscribe.objects.get(adding_user=self, added_user__id=user_id)
        subscribe.delete()

    def block_user_with_pk(self, pk):
        user = User.objects.get(pk=pk)
        return self.block_user_with_id(user_id=user.pk)

    def block_user_with_id(self, user_id):
        from users.model.list import UserBlock
        if user_id == self.pk:
            raise ValidationError('Вы не можете блокировать себя')
            if self.is_blocked_with_user_with_id(user_id=user_id):
                raise PermissionDenied('Вы в черном списке у этого пользователя.')

        if self.is_adding_user_with_id(user_id=user_id):
            self.unsubscribe_user_with_id(user_id=user_id)

        user_to_block = User.objects.get(pk=user_id)
        if user_to_block.is_adding_user_with_id(user_id=self.pk):
            user_to_block.unsubscribe_user_with_id(self.pk)

        UserBlock.create_user_block(blocker_id=self.pk, blocked_user_id=user_id)
        return user_to_block

    def unblock_user_with_pk(self, pk):
        user = User.objects.get(pk=pk)
        return self.unblock_user_with_id(user_id=user.pk)

    def unblock_user_with_id(self, user_id):
        if not self.has_blocked_user_with_id(user_id=user_id):
            raise ValidationError('Вы не можете разблокировать учетную запись, которую вы не заблокировали')
        self.user_blocks.filter(blocked_user_id=user_id).delete()
        return User.objects.get(pk=user_id)

    def get_last_location(self):
        from users.model.profile import OneUserLocation, TwoUserLocation, ThreeUserLocation

        if self.user_ip.ip_3:
            return ThreeUserLocation.objects.get(user=self)
        elif self.user_ip.ip_2:
            return TwoUserLocation.objects.get(user=self)
        elif self.user_ip.ip_1:
            return OneUserLocation.objects.get(user=self)
        else:
            return "Местоположение не указано"

    def get_my_ads(self):
        from ad_posts.models import Ad

        ads_query = Q(creator_id=self.id, is_deleted=False)
        ads = Ad.objects.filter(ads_query)
        return ads

    def get_ads(self):
        from ad_posts.models import Ad

        ads_query = Q(creator_id=self.id, is_deleted=False, is_active=True)
        ads = Ad.objects.filter(ads_query)
        return ads

    def get_my_courses(self):
        from skill_posts.models import Course

        courses_query = Q(creator_id=self.id, is_deleted=False)
        courses = Course.objects.filter(courses_query)
        return courses

    def get_courses(self):
        from skill_posts.models import Course

        courses_query = Q(creator_id=self.id, is_deleted=False, is_active=True)
        courses = Course.objects.filter(courses_query)
        return courses

    def get_my_ankets(self):
        from love_posts.models import Anketa

        courses_query = Q(creator_id=self.id, is_deleted=False)
        courses = Anketa.objects.filter(courses_query)
        return courses

    def get_ankets(self):
        from love_posts.models import Anketa

        courses_query = Q(creator_id=self.id, is_deleted=False, is_active=True)
        courses = Anketa.objects.filter(courses_query)
        return courses

    def get_my_favorite_ads(self):
        from ad_posts.models import Ad

        favorites_query = Q(adfavourites__user_id=self.id, is_active=True, is_sold=False, is_deleted=False)
        favorites_query.add(~Q(Q(adfavourites__user_id__blocked_by_users__blocker_id=self.id) | Q(adfavourites__user_id__user_blocks__blocked_user_id=self.id)), Q.AND)
        favorites = Ad.objects.filter(favorites_query)
        return favorites

    def get_my_blacklist(self):

        blacklist_query = Q(blocked_by_users__blocker_id=self.id, is_deleted=False)
        blacklist = User.objects.filter(blacklist_query)
        return blacklist

    def get_my_favorite_courses(self):
        from skill_posts.models import Course

        favorites_query = Q(coursefavourites__user_id=self.id, is_active=True, is_deleted=False)
        favorites_query.add(~Q(Q(coursefavourites__user_id__blocked_by_users__blocker_id=self.id) | Q(coursefavourites__user_id__user_blocks__blocked_user_id=self.id)), Q.AND)
        favorites = Course.objects.filter(favorites_query)
        return favorites

    def get_my_favorite_anketa(self):
        from love_posts.models import Anketa

        favorites_query = Q(anketafavourites__user_id=self.id, is_active=True, is_deleted=False)
        favorites_query.add(~Q(Q(anketafavourites__user_id__blocked_by_users__blocker_id=self.id) | Q(anketafavourites__user_id__user_blocks__blocked_user_id=self.id)), Q.AND)
        favorites = Anketa.objects.filter(favorites_query)
        return favorites

    def get_subscribs(self):
        """Это те, кто на меня подписался"""

        subscribs_query = Q(adding_user__added_user__id=self.id, is_deleted=False)
        subscribs_query.add(~Q(Q(blocked_by_users__blocker_id=self.id) | Q(user_blocks__blocked_user_id=self.id)), Q.AND)
        subscribs = User.objects.filter(subscribs_query)
        return subscribs

    def get_my_subscribs(self):
        """Это те, на кого я подписался"""

        subscribs_query = Q(added_user__adding_user__id=self.id, is_deleted=False)
        subscribs_query.add(~Q(Q(blocked_by_users__blocker_id=self.id) | Q(user_blocks__blocked_user_id=self.id)), Q.AND)
        subscribs = User.objects.filter(subscribs_query)
        return subscribs

    def get_ads_managers(self):
        from users.model.profile import UserAdStaff
        managers = UserAdStaff.objects.filter(Q(Q(is_administrator=True) | Q(is_moderator=True) | Q(is_editor=True) | Q(is_advertiser=True))).values('user_id')
        managers_ids = [user['user_id'] for user in managers]
        users = Q(id__in=managers_ids)
        exclude_superuser = ~Q(is_superuser=True)
        users.add(exclude_superuser, Q.AND)
        managers_query = User.objects.filter(users)
        return managers_query

    def get_skills_managers(self):
        from users.model.profile import UserSkillStaff
        managers = UserSkillStaff.objects.filter(Q(Q(is_administrator=True) | Q(is_moderator=True) | Q(is_editor=True) | Q(is_advertiser=True)| Q(is_teacher=True))).values('user_id')
        managers_ids = [user['user_id'] for user in managers]
        users = Q(id__in=managers_ids)
        exclude_superuser = ~Q(is_superuser=True)
        users.add(exclude_superuser, Q.AND)
        managers_query = User.objects.filter(users)
        return managers_query

    def get_ankets_managers(self):
        from users.model.profile import UserAnketaStaff
        managers = UserAnketaStaff.objects.filter(Q(Q(is_administrator=True) | Q(is_moderator=True) | Q(is_editor=True) | Q(is_advertiser=True))).values('user_id')
        managers_ids = [user['user_id'] for user in managers]
        users = Q(id__in=managers_ids)
        exclude_superuser = ~Q(is_superuser=True)
        users.add(exclude_superuser, Q.AND)
        managers_query = User.objects.filter(users)
        return managers_query

    def get_managers(self):
        from users.model.profile import UserStaff
        managers = UserStaff.objects.filter(Q(Q(is_administrator=True) | Q(is_moderator=True) | Q(is_editor=True) | Q(is_advertiser=True))).values('user_id')
        managers_ids = [user['user_id'] for user in managers]
        users = Q(id__in=managers_ids)
        exclude_superuser = ~Q(is_superuser=True)
        users.add(exclude_superuser, Q.AND)
        managers_query = User.objects.filter(users)
        return managers_query

    def add_skill_administrator(self):
        from users.model.profile import UserSkillStaff
        try:
            user_staff = UserSkillStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.is_administrator = True
            user_staff.is_editor = False
            user_staff.is_advertiser = False
            user_staff.save()
        except:
            user_staff = UserSkillStaff.objects.create(user=self, is_administrator=True)
        return user_staff
    def add_skill_moderator(self):
        from users.model.profile import UserSkillStaff
        try:
            user_staff = UserSkillStaff.objects.get(user=self)
            user_staff.is_moderator = True
            user_staff.is_administrator = False
            user_staff.is_editor = False
            user_staff.is_advertiser = False
            user_staff.save()
        except:
            user_staff = UserSkillStaff.objects.create(user=self, is_moderator=True)
        return user_staff
    def add_skill_editor(self):
        from users.model.profile import UserSkillStaff
        try:
            user_staff = UserSkillStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.is_administrator = False
            user_staff.is_editor = True
            user_staff.is_advertiser = False
            user_staff.save()
        except:
            user_staff = UserSkillStaff.objects.create(user=self, is_editor=True)
        return user_staff
    def add_skill_advertiser(self):
        from users.model.profile import UserSkillStaff
        try:
            user_staff = UserSkillStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.is_administrator = False
            user_staff.is_editor = False
            user_staff.is_advertiser = True
            user_staff.save()
        except:
            user_staff = UserSkillStaff.objects.create(user=self, is_advertiser=True)
        return user_staff
    def add_skill_teacher(self):
        from users.model.profile import UserSkillStaff
        try:
            user_staff = UserSkillStaff.objects.get(user=self)
            user_staff.is_teacher = True
            user_staff.save()
        except:
            user_staff = UserSkillStaff.objects.create(user=self, is_teacher=True)
        return user_staff

    def remove_skill_administrator(self):
        from users.model.profile import UserSkillStaff
        try:
            user_staff = UserSkillStaff.objects.get(user=self)
            user_staff.is_administrator = False
            user_staff.save(update_fields=['is_administrator'])
            return user_staff
        except:
            pass
    def remove_skill_moderator(self):
        from users.model.profile import UserSkillStaff
        try:
            user_staff = UserSkillStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.save(update_fields=['is_moderator'])
            return user_staff
        except:
            pass
    def remove_skill_editor(self):
        from users.model.profile import UserSkillStaff
        try:
            user_staff = UserSkillStaff.objects.get(user=self)
            user_staff.is_editor = False
            user_staff.save(update_fields=['is_editor'])
            return user_staff
        except:
            pass
    def remove_skill_advertiser(self):
        from users.model.profile import UserSkillStaff
        try:
            user_staff = UserSkillStaff.objects.get(user=self)
            user_staff.is_advertiser = False
            user_staff.save(update_fields=['is_advertiser'])
            return user_staff
        except:
            pass
    def remove_skill_teacher(self):
        from users.model.profile import UserSkillStaff
        try:
            user_staff = UserSkillStaff.objects.get(user=self)
            user_staff.is_teacher = False
            user_staff.save()
            return user_staff
        except:
            pass

    def add_ad_administrator(self):
        from users.model.profile import UserAdStaff
        try:
            user_staff = UserAdStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.is_administrator = True
            user_staff.is_editor = False
            user_staff.is_advertiser = False
            user_staff.save()
        except:
            user_staff = UserAdStaff.objects.create(user=self, is_administrator=True)
        return user_staff
    def add_ad_moderator(self):
        from users.model.profile import UserAdStaff
        try:
            user_staff = UserAdStaff.objects.get(user=self)
            user_staff.is_moderator = True
            user_staff.is_administrator = False
            user_staff.is_editor = False
            user_staff.is_advertiser = False
            user_staff.save()
        except:
            user_staff = UserAdStaff.objects.create(user=self, is_moderator=True)
        return user_staff
    def add_ad_editor(self):
        from users.model.profile import UserAdStaff
        try:
            user_staff = UserAdStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.is_administrator = False
            user_staff.is_editor = True
            user_staff.is_advertiser = False
            user_staff.save()
        except:
            user_staff = UserAdStaff.objects.create(user=self, is_editor=True)
        return user_staff
    def add_ad_advertiser(self):
        from users.model.profile import UserAdStaff
        try:
            user_staff = UserAdStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.is_administrator = False
            user_staff.is_editor = False
            user_staff.is_advertiser = True
            user_staff.save()
        except:
            user_staff = UserAdStaff.objects.create(user=self, is_advertiser=True)
        return user_staff

    def remove_ad_administrator(self):
        from users.model.profile import UserAdStaff
        try:
            user_staff = UserAdStaff.objects.get(user=self)
            user_staff.is_administrator = False
            user_staff.save(update_fields=['is_administrator'])
            return user_staff
        except:
            pass
    def remove_ad_moderator(self):
        from users.model.profile import UserAdStaff
        try:
            user_staff = UserAdStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.save(update_fields=['is_moderator'])
            return user_staff
        except:
            pass
    def remove_ad_editor(self):
        from users.model.profile import UserAdStaff
        try:
            user_staff = UserAdStaff.objects.get(user=self)
            user_staff.is_editor = False
            user_staff.save(update_fields=['is_editor'])
            return user_staff
        except:
            pass
    def remove_ad_advertiser(self):
        from users.model.profile import UserAdStaff
        try:
            user_staff = UserAdStaff.objects.get(user=self)
            user_staff.is_advertiser = False
            user_staff.save(update_fields=['is_advertiser'])
            return user_staff
        except:
            pass


    def add_user_administrator(self):
        from users.model.profile import UserStaff
        try:
            user_staff = UserStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.is_administrator = True
            user_staff.is_editor = False
            user_staff.is_advertiser = False
            user_staff.save()
        except:
            user_staff = UserStaff.objects.create(user=self, is_administrator=True)
        return user_staff
    def add_user_moderator(self):
        from users.model.profile import UserStaff
        try:
            user_staff = UserStaff.objects.get(user=self)
            user_staff.is_moderator = True
            user_staff.is_administrator = False
            user_staff.is_editor = False
            user_staff.is_advertiser = False
            user_staff.save()
        except:
            user_staff = UserStaff.objects.create(user=self, is_moderator=True)
        return user_staff
    def add_user_editor(self):
        from users.model.profile import UserStaff
        try:
            user_staff = UserStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.is_administrator = False
            user_staff.is_editor = True
            user_staff.is_advertiser = False
            user_staff.save()
        except:
            user_staff = UserStaff.objects.create(user=self, is_editor=True)
        return user_staff
    def add_user_advertiser(self):
        from users.model.profile import UserStaff
        try:
            user_staff = UserStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.is_administrator = False
            user_staff.is_editor = False
            user_staff.is_advertiser = True
            user_staff.save()
        except:
            user_staff = UserStaff.objects.create(user=self, is_advertiser=True)
        return user_staff

    def remove_user_administrator(self):
        from users.model.profile import UserStaff
        try:
            user_staff = UserStaff.objects.get(user=self)
            user_staff.is_administrator = False
            user_staff.save(update_fields=['is_administrator'])
            return user_staff
        except:
            pass
    def remove_user_moderator(self):
        from users.model.profile import UserStaff
        try:
            user_staff = UserStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.save(update_fields=['is_moderator'])
            return user_staff
        except:
            pass
    def remove_user_editor(self):
        from users.model.profile import UserStaff
        try:
            user_staff = UserStaff.objects.get(user=self)
            user_staff.is_editor = False
            user_staff.save(update_fields=['is_editor'])
            return user_staff
        except:
            pass
    def remove_user_advertiser(self):
        from users.model.profile import UserStaff
        try:
            user_staff = UserStaff.objects.get(user=self)
            user_staff.is_advertiser = False
            user_staff.save(update_fields=['is_advertiser'])
            return user_staff
        except:
            pass


    def add_anketa_administrator(self):
        from users.model.profile import UserAnketaStaff
        try:
            user_staff = UserAnketaStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.is_administrator = True
            user_staff.is_editor = False
            user_staff.is_advertiser = False
            user_staff.save()
        except:
            user_staff = UserAnketaStaff.objects.create(user=self, is_administrator=True)
        return user_staff
    def add_anketa_moderator(self):
        from users.model.profile import UserAnketaStaff
        try:
            user_staff = UserAnketaStaff.objects.get(user=self)
            user_staff.is_moderator = True
            user_staff.is_administrator = False
            user_staff.is_editor = False
            user_staff.is_advertiser = False
            user_staff.save()
        except:
            user_staff = UserAnketaStaff.objects.create(user=self, is_moderator=True)
        return user_staff
    def add_anketa_editor(self):
        from users.model.profile import UserAnketaStaff
        try:
            user_staff = UserAnketaStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.is_administrator = False
            user_staff.is_editor = True
            user_staff.is_advertiser = False
            user_staff.save()
        except:
            user_staff = UserAnketaStaff.objects.create(user=self, is_editor=True)
        return user_staff
    def add_anketa_advertiser(self):
        from users.model.profile import UserAnketaStaff
        try:
            user_staff = UserAnketaStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.is_administrator = False
            user_staff.is_editor = False
            user_staff.is_advertiser = True
            user_staff.save()
        except:
            user_staff = UserAnketaStaff.objects.create(user=self, is_advertiser=True)
        return user_staff

    def remove_anketa_administrator(self):
        from users.model.profile import UserAnketaStaff
        try:
            user_staff = UserAnketaStaff.objects.get(user=self)
            user_staff.is_administrator = False
            user_staff.save(update_fields=['is_administrator'])
            return user_staff
        except:
            pass
    def remove_anketa_moderator(self):
        from users.model.profile import UserAnketaStaff
        try:
            user_staff = UserAnketaStaff.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.save(update_fields=['is_moderator'])
            return user_staff
        except:
            pass
    def remove_anketa_editor(self):
        from users.model.profile import UserAnketaStaff
        try:
            user_staff = UserAnketaStaff.objects.get(user=self)
            user_staff.is_editor = False
            user_staff.save(update_fields=['is_editor'])
            return user_staff
        except:
            pass
    def remove_anketa_advertiser(self):
        from users.model.profile import UserAnketaStaff
        try:
            user_staff = UserAnketaStaff.objects.get(user=self)
            user_staff.is_advertiser = False
            user_staff.save(update_fields=['is_advertiser'])
            return user_staff
        except:
            pass

    def add_ad_administrator_worker(self, request_user):
        from users.model.profile import CanAddStaffAdUser
        try:
            user_staff = CanAddStaffAdUser.objects.get(user=self)
            user_staff.is_administrator = True
            user_staff.save(update_fields=['is_administrator'])
        except:
            user_staff = CanAddStaffAdUser.objects.create(user=self, is_administrator=True)
        return user_staff
    def add_ad_moderator_worker(self):
        from users.model.profile import CanAddStaffAdUser
        try:
            user_staff = CanAddStaffAdUser.objects.get(user=self)
            user_staff.is_moderator = True
            user_staff.save(update_fields=['is_moderator'])
        except:
            user_staff = CanAddStaffAdUser.objects.create(user=self, is_moderator=True)
        return user_staff
    def add_ad_editor_worker(self):
        from users.model.profile import CanAddStaffAdUser
        try:
            user_staff = CanAddStaffAdUser.objects.get(user=self)
            user_staff.is_editor = True
            user_staff.save(update_fields=['is_editor'])
        except:
            user_staff = CanAddStaffAdUser.objects.create(user=self, is_editor=True)
        return user_staff
    def add_ad_advirtiser_worker(self):
        from users.model.profile import CanAddStaffAdUser
        try:
            user_staff = CanAddStaffAdUser.objects.get(user=self)
            user_staff.is_advirtiser = True
            user_staff.save(update_fields=['is_advirtiser'])
        except:
            user_staff = CanAddStaffAdUser.objects.create(user=self, is_advertiser=True)
        return user_staff

    def remove_ad_administrator_worker(self):
        from users.model.profile import CanAddStaffAdUser
        try:
            user_staff = CanAddStaffAdUser.objects.get(user=self)
            user_staff.is_administrator = False
            user_staff.save(update_fields=['is_administrator'])
            return user_staff
        except:
            pass
    def remove_ad_moderator_worker(self):
        from users.model.profile import CanAddStaffAdUser
        try:
            user_staff = CanAddStaffAdUser.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.save(update_fields=['is_moderator'])
            return user_staff
        except:
            pass
    def remove_ad_editor_worker(self):
        from users.model.profile import CanAddStaffAdUser
        try:
            user_staff = CanAddStaffAdUser.objects.get(user=self)
            user_staff.is_editor = False
            user_staff.save(update_fields=['is_editor'])
            return user_staff
        except:
            pass
    def remove_ad_advirtiser_worker(self):
        from users.model.profile import CanAddStaffAdUser
        try:
            user_staff = CanAddStaffAdUser.objects.get(user=self)
            user_staff.is_advirtiser = False
            user_staff.save(update_fields=['is_advirtiser'])
            return user_staff
        except:
            pass


    def add_skill_administrator_worker(self):
        from users.model.profile import CanAddStaffSkillUser
        try:
            user_staff = CanAddStaffSkillUser.objects.get(user=self)
            user_staff.is_administrator = True
            user_staff.save(update_fields=['is_administrator'])
        except:
            user_staff = CanAddStaffSkillUser.objects.create(user=self, is_administrator=True)
        return user_staff
    def add_skill_moderator_worker(self):
        from users.model.profile import CanAddStaffSkillUser
        try:
            user_staff = CanAddStaffSkillUser.objects.get(user=self)
            user_staff.is_moderator = True
            user_staff.save(update_fields=['is_moderator'])
        except:
            user_staff = CanAddStaffSkillUser.objects.create(user=self, is_moderator=True)
        return user_staff
    def add_skill_editor_worker(self):
        from users.model.profile import CanAddStaffSkillUser
        try:
            user_staff = CanAddStaffSkillUser.objects.get(user=self)
            user_staff.is_editor = True
            user_staff.save(update_fields=['is_editor'])
        except:
            user_staff = CanAddStaffSkillUser.objects.create(user=self, is_editor=True)
        return user_staff
    def add_skill_advirtiser_worker(self):
        from users.model.profile import CanAddStaffSkillUser
        try:
            user_staff = CanAddStaffSkillUser.objects.get(user=self)
            user_staff.is_advirtiser = True
            user_staff.save(update_fields=['is_advirtiser'])
        except:
            user_staff = CanAddStaffSkillUser.objects.create(user=self, is_advertiser=True)
        return user_staff
    def add_skill_teacher_worker(self):
        from users.model.profile import CanAddStaffSkillUser
        try:
            user_staff = CanAddStaffSkillUser.objects.get(user=self)
            user_staff.is_teacher = True
            user_staff.save(update_fields=['is_teacher'])
        except:
            user_staff = CanAddStaffSkillUser.objects.create(user=self, is_teacher=True)
        return user_staff

    def remove_skill_administrator_worker(self):
        from users.model.profile import CanAddStaffSkillUser
        try:
            user_staff = CanAddStaffSkillUser.objects.get(user=self)
            user_staff.is_administrator = False
            user_staff.save(update_fields=['is_administrator'])
            return user_staff
        except:
            pass
    def remove_skill_moderator_worker(self):
        from users.model.profile import CanAddStaffSkillUser
        try:
            user_staff = CanAddStaffSkillUser.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.save(update_fields=['is_moderator'])
            return user_staff
        except:
            pass
    def remove_skill_editor_worker(self):
        from users.model.profile import CanAddStaffSkillUser
        try:
            user_staff = CanAddStaffSkillUser.objects.get(user=self)
            user_staff.is_editor = False
            user_staff.save(update_fields=['is_editor'])
            return user_staff
        except:
            pass
    def remove_skill_advirtiser_worker(self):
        from users.model.profile import CanAddStaffSkillUser
        try:
            user_staff = CanAddStaffSkillUser.objects.get(user=self)
            user_staff.is_advirtiser = False
            user_staff.save(update_fields=['is_advirtiser'])
            return user_staff
        except:
            pass
    def remove_skill_teacher_worker(self):
        from users.model.profile import CanAddStaffSkillUser
        try:
            user_staff = CanAddStaffSkillUser.objects.get(user=self)
            user_staff.is_teacher = False
            user_staff.save(update_fields=['is_teacher'])
            return user_staff
        except:
            pass


    def add_anketa_administrator_worker(self):
        from users.model.profile import CanAddStaffAnketaUser
        try:
            user_staff = CanAddStaffAnketaUser.objects.get(user=self)
            user_staff.is_administrator = True
            user_staff.save(update_fields=['is_administrator'])
        except:
            user_staff = CanAddStaffAnketaUser.objects.create(user=self, is_administrator=True)
        return user_staff
    def add_anketa_moderator_worker(self):
        from users.model.profile import CanAddStaffAnketaUser
        try:
            user_staff = CanAddStaffAnketaUser.objects.get(user=self)
            user_staff.is_moderator = True
            user_staff.save(update_fields=['is_moderator'])
        except:
            user_staff = CanAddStaffAnketaUser.objects.create(user=self, is_moderator=True)
        return user_staff
    def add_anketa_editor_worker(self):
        from users.model.profile import CanAddStaffAnketaUser
        try:
            user_staff = CanAddStaffAnketaUser.objects.get(user=self)
            user_staff.is_editor = True
            user_staff.save(update_fields=['is_editor'])
        except:
            user_staff = CanAddStaffAnketaUser.objects.create(user=self, is_editor=True)
        return user_staff
    def add_anketa_advirtiser_worker(self):
        from users.model.profile import CanAddStaffAnketaUser
        try:
            user_staff = CanAddStaffAnketaUser.objects.get(user=self)
            user_staff.is_advirtiser = True
            user_staff.save(update_fields=['is_advirtiser'])
        except:
            user_staff = CanAddStaffAnketaUser.objects.create(user=self, is_advertiser=True)
        return user_staff

    def remove_anketa_administrator_worker(self):
        from users.model.profile import CanAddStaffAnketaUser
        try:
            user_staff = CanAddStaffAnketaUser.objects.get(user=self)
            user_staff.is_administrator = False
            user_staff.save(update_fields=['is_administrator'])
            return user_staff
        except:
            pass
    def remove_anketa_moderator_worker(self):
        from users.model.profile import CanAddStaffAnketaUser
        try:
            user_staff = CanAddStaffAnketaUser.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.save(update_fields=['is_moderator'])
            return user_staff
        except:
            pass
    def remove_anketa_editor_worker(self):
        from users.model.profile import CanAddStaffAnketaUser
        try:
            user_staff = CanAddStaffAnketaUser.objects.get(user=self)
            user_staff.is_editor = False
            user_staff.save(update_fields=['is_editor'])
            return user_staff
        except:
            pass
    def remove_anketa_advirtiser_worker(self):
        from users.model.profile import CanAddStaffAnketaUser
        try:
            user_staff = CanAddStaffAnketaUser.objects.get(user=self)
            user_staff.is_advirtiser = False
            user_staff.save(update_fields=['is_advirtiser'])
            return user_staff
        except:
            pass


    def add_user_administrator_worker(self, request_user):
        from users.model.profile import CanAddStaffUser
        try:
            user_staff = CanAddStaffUser.objects.get(user=self)
            user_staff.is_administrator = True
            user_staff.save(update_fields=['is_administrator'])
        except:
            user_staff = CanAddStaffUser.objects.create(user=self, is_administrator=True)
        return user_staff
    def add_user_moderator_worker(self):
        from users.model.profile import CanAddStaffUser
        try:
            user_staff = CanAddStaffUser.objects.get(user=self)
            user_staff.is_moderator = True
            user_staff.save(update_fields=['is_moderator'])
        except:
            user_staff = CanAddStaffUser.objects.create(user=self, is_moderator=True)
        return user_staff
    def add_user_editor_worker(self):
        from users.model.profile import CanAddStaffUser
        try:
            user_staff = CanAddStaffUser.objects.get(user=self)
            user_staff.is_editor = True
            user_staff.save(update_fields=['is_editor'])
        except:
            user_staff = CanAddStaffUser.objects.create(user=self, is_editor=True)
        return user_staff
    def add_user_advirtiser_worker(self):
        from users.model.profile import CanAddStaffUser
        try:
            user_staff = CanAddStaffUser.objects.get(user=self)
            user_staff.is_advirtiser = True
            user_staff.save(update_fields=['is_advirtiser'])
        except:
            user_staff = CanAddStaffUser.objects.create(user=self, is_advertiser=True)
        return user_staff

    def remove_user_administrator_worker(self):
        from users.model.profile import CanAddStaffUser
        try:
            user_staff = CanAddStaffUser.objects.get(user=self)
            user_staff.is_administrator = False
            user_staff.save(update_fields=['is_administrator'])
            return user_staff
        except:
            pass
    def remove_user_moderator_worker(self):
        from users.model.profile import CanAddStaffUser
        try:
            user_staff = CanAddStaffUser.objects.get(user=self)
            user_staff.is_moderator = False
            user_staff.save(update_fields=['is_moderator'])
            return user_staff
        except:
            pass
    def remove_user_editor_worker(self):
        from users.model.profile import CanAddStaffUser
        try:
            user_staff = CanAddStaffUser.objects.get(user=self)
            user_staff.is_editor = False
            user_staff.save(update_fields=['is_editor'])
            return user_staff
        except:
            pass
    def remove_user_advirtiser_worker(self):
        from users.model.profile import CanAddStaffUser
        try:
            user_staff = CanAddStaffUser.objects.get(user=self)
            user_staff.is_advirtiser = False
            user_staff.save(update_fields=['is_advirtiser'])
            return user_staff
        except:
            pass
