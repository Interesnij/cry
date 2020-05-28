from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound, AuthenticationFailed
from communities.models import Community
from invitations.models import UserInvite
from main.models import Item, ItemComment
import jwt
from django.conf import settings


''''' communities '''''

def check_can_post_to_community_with_name(user, community_name=None):
    if not user.is_member_of_community_with_name(community_name=community_name):
        raise ValidationError(
            'Вы не можете публиковать записи в сообществе, членом которого Вы не являетесь',
        )


def check_can_enable_disable_comments_for_post_in_community_with_name(user, community_name):
    if not user.is_moderator_of_community_with_name(community_name) and \
            not user.is_administrator_of_community_with_name(community_name):
        raise ValidationError(
            'Только администраторы / модераторы могут включать / выключать комментарии к записи сообщества',
        )


def check_can_delete_community_with_name(user, community_name):
    if not user.is_creator_of_community_with_name(community_name):
        raise ValidationError(
            'Не удается удалить сообщество, которое вы не администрируете.',
        )


def check_can_update_community_with_name(user, community_name):
    if not user.is_administrator_of_community_with_name(community_name):
        raise ValidationError(
            'Не удается обновить сообщество, которое вы не администрируете.',
        )


def check_can_get_posts_for_community_with_name(user, community_name):
    check_is_not_banned_from_community_with_name(user=user, community_name=community_name)
    if Community.is_community_with_name_private(
            community_name=community_name) and not user.is_member_of_community_with_name(
        community_name=community_name):
        raise ValidationError(
            'Сообщество является приватным. Вы должны стать участником, чтобы видеть его записи.',
        )
    if Community.is_community_with_name_closed(
            community_name=community_name) and not user.is_member_of_community_with_name(
        community_name=community_name):
        raise ValidationError(
            'Сообщество является закрытым. Вы должны стать участником, чтобы видеть его записи.',
        )


def check_can_get_closed_posts_for_community_with_name(user, community_name):
    if not user.is_administrator_of_community_with_name(community_name=community_name) and \
            not user.is_moderator_of_community_with_name(community_name=community_name):
        raise ValidationError(
            'Только администраторы/модераторы могут просматривать закрытые записи',
        )


def check_can_get_community_with_name_members(user, community_name):
    check_is_not_banned_from_community_with_name(user=user, community_name=community_name)

    if Community.is_community_with_name_private(community_name=community_name):
        if not user.is_member_of_community_with_name(community_name=community_name):
            raise ValidationError(
                'Нельзя видеть подписчиков частного сообщества.',
            )


def check_can_join_community_with_name(user, community_name):
    if user.is_banned_from_community_with_name(community_name):
        raise ValidationError('Вы не можете присоединиться к сообществу, в котором вы были заблокированы.')

    if user.is_member_of_community_with_name(community_name):
        raise ValidationError(
            'Вы уже являетесь подписчиков сообщества',
        )

    if Community.is_community_with_name_private(community_name=community_name):
        if not user.is_invited_to_community_with_name(community_name=community_name):
            raise ValidationError(
                'Вы не приглашены в это сообщество',
            )


def check_can_leave_community_with_name(user, community_name):
    if not user.is_member_of_community_with_name(community_name=community_name):
        raise ValidationError(
            'Вы не можете покинуть сообщество, подписчиком которого Вы не являетесь.',
        )

    if user.is_creator_of_community_with_name(community_name=community_name):
        raise ValidationError(
            'Вы не можете покинуть созданное Вами сообщество.',
        )


def check_can_invite_user_with_username_to_community_with_name(user, username, community_name):
    if not user.is_member_of_community_with_name(community_name=community_name):
        raise ValidationError(
            'Вы можете приглашать людей только в сообщество, членом которого являетесь.',
        )

    if user.has_invited_user_with_username_to_community_with_name(username=username, community_name=community_name):
        raise ValidationError(
            'Вы уже пригласили этого пользователя присоединиться к сообществу.',
        )

    if Community.is_user_with_username_member_of_community_with_name(username=username,
                                                                     community_name=community_name):
        raise ValidationError(
            'Пользователь уже является подписчиком сообщества',
        )

    if not Community.is_community_with_name_invites_enabled(community_name=community_name) and not (
            user.is_administrator_of_community_with_name(
                community_name=community_name) or user.is_moderator_of_community_with_name(
        community_name=community_name)):
        raise ValidationError(
            'Приглашения для этого сообщества не включены. Приглашать могут только администраторы и модераторы.',
        )


def check_can_uninvite_user_with_username_to_community_with_name(user, username, community_name):
    if not user.has_invited_user_with_username_to_community_with_name(username=username,
                                                                      community_name=community_name):
        raise ValidationError(
            'Никаких приглашений не найдено',
        )


def check_can_get_community_with_name_banned_users(user, community_name):
    if not user.is_administrator_of_community_with_name(
            community_name=community_name) and not user.is_moderator_of_community_with_name(
        community_name=community_name):
        raise ValidationError(
            'Только администраторы и модераторы сообщества могут видеть заблокированных пользователей.',
        )


def check_can_ban_user_with_username_from_community_with_name(user, username, community_name):
    if not user.is_administrator_of_community_with_name(
            community_name=community_name) and not user.is_moderator_of_community_with_name(
        community_name=community_name):
        raise ValidationError(
            'Только администраторы и модераторы сообщества могут блокировать участников сообщества.',
        )

    if Community.is_user_with_username_banned_from_community_with_name(username=username,
                                                                       community_name=community_name):
        raise ValidationError(
            'Пользователь уже забанен',
        )

    if Community.is_user_with_username_moderator_of_community_with_name(username=username,
                                                                        community_name=community_name) or Community.is_user_with_username_administrator_of_community_with_name(
        username=username, community_name=community_name):
        raise ValidationError(
            'Вы не можете заблокировать модератора или администратора сообщества',
        )


def check_can_unban_user_with_username_from_community_with_name(user, username, community_name):
    if not user.is_administrator_of_community_with_name(
            community_name=community_name) and not user.is_moderator_of_community_with_name(
        community_name=community_name):
        raise ValidationError(
            'Только администраторы и модераторы сообщества могут блокировать участников сообщества',
        )
    if not Community.is_user_with_username_banned_from_community_with_name(username=username,
                                                                           community_name=community_name):
        raise ValidationError(
            'Нельзя разбанить не заблокированного пользователя',
        )


def check_can_add_administrator_with_username_to_community_with_name(user, username, community_name):
    if not user.is_creator_of_community_with_name(community_name=community_name):
        raise ValidationError(
            'Только создатель сообщества может добавить администраторов.',
        )

    if Community.is_user_with_username_administrator_of_community_with_name(username=username,
                                                                            community_name=community_name):
        raise ValidationError(
            'Пользователь уже является администратором',
        )

    if not Community.is_user_with_username_member_of_community_with_name(username=username,
                                                                        community_name=community_name):
        raise ValidationError(
            'Нельзя сделать администратором пользователя, который не подписан на сообщество',
        )


def check_can_remove_administrator_with_username_to_community_with_name(user, username, community_name):
    if not user.is_creator_of_community_with_name(community_name=community_name):
        raise ValidationError(
            'Только создатель сообщества может удалить администраторов.',
        )

    if not Community.is_user_with_username_administrator_of_community_with_name(username=username,
                                                                                community_name=community_name):
        raise ValidationError(
            'Пользователь не является администратором',
        )


def check_can_get_community_with_name_administrators(user, community_name):
    check_is_not_banned_from_community_with_name(user=user, community_name=community_name)


def check_can_add_moderator_with_username_to_community_with_name(user, username, community_name):
    if not user.is_administrator_of_community_with_name(community_name=community_name):
        raise ValidationError(
            'Только администраторы сообщества могут добавлять модераторов',
        )

    if Community.is_user_with_username_administrator_of_community_with_name(username=username,
                                                                            community_name=community_name):
        raise ValidationError(
            'Пользователь является администратором',
        )

    if Community.is_user_with_username_moderator_of_community_with_name(username=username,
                                                                        community_name=community_name):
        raise ValidationError(
            'Пользователь уже является модератором',
        )

    if not Community.is_user_with_username_member_of_community_with_name(username=username,
                                                                         community_name=community_name):
        raise ValidationError(
            'Нельзя сделать модератором пользователя, который не является подписчиком сообщества',
        )


def check_can_remove_moderator_with_username_to_community_with_name(user, username, community_name):
    if not user.is_administrator_of_community_with_name(community_name=community_name):
        raise ValidationError(
            'Удалять модераторов могут только администраторы сообщества',
        )

    if not Community.is_user_with_username_moderator_of_community_with_name(username=username,
                                                                            community_name=community_name):
        raise ValidationError(
            'Пользователь не является модератором',
        )


def check_can_get_community_with_name_moderators(user, community_name):
    check_is_not_banned_from_community_with_name(user=user, community_name=community_name)


def check_is_not_banned_from_community_with_name(user, community_name):
    if user.is_banned_from_community_with_name(community_name):
        raise PermissionDenied('Вы заблокированы в этом сообществе')


def check_can_favorite_community_with_name(user, community_name):
    if not user.is_member_of_community_with_name(community_name=community_name):
        raise ValidationError(
            'Вы должны быть членом сообщества, прежде чем сделать его избранным',
        )

    if user.has_favorite_community_with_name(community_name=community_name):
        raise ValidationError(
            'Вы уже отметили это сообщество как избранное',
        )


def check_can_exclude_community(user, community):
    if user.has_excluded_community_with_name(community_name=community.name):
        raise ValidationError(
            'Вы уже отметили это сообщество как исключенное',
        )

    if community.type == Community.COMMUNITY_TYPE_PRIVATE:
        raise ValidationError(
            'Частные сообщества не могут создавать особые записи',
        )


def check_can_remove_exclusion_for_community(user, community):
    if not user.has_excluded_community_with_name(community_name=community.name):
        raise ValidationError(
            'Вы не отметили это сообщество как исключенное',
        )


def check_can_unfavorite_community_with_name(user, community_name):
    if not user.has_favorite_community_with_name(community_name=community_name):
        raise ValidationError(
            'Вы не фаворит общества',
        )


def check_can_get_community_with_name(user, community_name):
    check_is_not_banned_from_community_with_name(user=user, community_name=community_name)


def check_is_staff_of_community_with_name(user, community_name):
    if not user.is_staff_of_community_with_name(community_name=community_name):
        raise PermissionDenied('Не персонал сообщества')


''''' follows '''''

def check_can_follow_user_with_id(user, user_id):
    check_is_not_blocked_with_user_with_id(user=user, user_id=user_id)
    check_is_not_following_user_with_id(user_id=user_id, user=user)
    check_has_not_reached_max_follows(user=user)

def check_not_can_follow_user_with_id(user, user_id):
    check_is_not_blocked_with_user_with_id(user=user, user_id=user_id)
    check_is_following_user_with_id(user=user, user_id=user_id)
    check_has_not_reached_max_follows(user=user)


def check_is_not_blocked_with_user_with_id(user, user_id):
    if user.is_blocked_with_user_with_id(user_id=user_id):
        raise PermissionDenied('Вы в черном списке у этого пользователя.')


def check_is_not_following_user_with_id(user, user_id):
    if user.is_following_user_with_id(user_id):
        raise ValidationError(
            'Пользователь уже подписан',
        )

def check_is_following_user_with_id(user, user_id):
    if not user.is_following_user_with_id(user_id):
        return True


def check_has_not_reached_max_follows(user):
    if user.count_following() > settings.USER_MAX_FOLLOWS:
        raise ValidationError(
            'Достигнуто максимальное количество подписчиков',
        )


def check_is_not_following_user_with_id(user, user_id):
    if not user.is_following_user_with_id(user_id):
        return True

''''' frends '''''

def check_has_not_reached_max_connections(user):
    if user.count_connections() > settings.USER_MAX_CONNECTIONS:
        raise ValidationError(
            'Достигнуто максимальное количество друзей',
        )


def check_can_connect_with_user_with_id(user, user_id):
    check_is_not_blocked_with_user_with_id(user=user, user_id=user_id)
    check_is_not_connected_with_user_with_id(user=user, user_id=user_id)
    check_has_not_reached_max_connections(user=user)


def check_is_not_connected_with_user_with_id(user, user_id):
    if user.is_connected_with_user_with_id(user_id):
        raise ValidationError(
            'Пользователь уже в друзьях',
        )


def check_is_connected_with_user_with_id(user, user_id):
    if not user.is_connected_with_user_with_id(user_id):
        raise ValidationError(
            'Не дружит с пользователем.',
        )


''''' invitations '''''

def check_can_create_invite(user, nickname):
    if user.invite_count == 0:
        raise ValidationError('У вас не осталось приглашений')

    if UserInvite.objects.filter(invited_by=user, nickname=nickname).exists():
        raise ValidationError('Ник уже используется')


def check_can_update_invite(user, invite_id):
    check_is_creator_of_invite_with_id(user=user, invite_id=invite_id)


def check_can_send_email_invite_to_invite_id(user, invite_id, email):
    check_is_creator_of_invite_with_id(user=user, invite_id=invite_id)
    invite = UserInvite.objects.get(id=invite_id)
    if invite.email == email:
        raise ValidationError('Приглашение по электронной почте уже отправлено на этот адрес')


def check_can_delete_invite_with_id(user, invite_id):
    check_is_creator_of_invite_with_id(user=user, invite_id=invite_id)
    check_if_invite_is_not_used(user=user, invite_id=invite_id)


def check_if_invite_is_not_used(user, invite_id):
    invite = UserInvite.objects.get(id=invite_id)
    if invite.created_user:
        raise ValidationError('Приглашение уже используется и не может быть удалено')


def check_is_creator_of_invite_with_id(user, invite_id):
    if not UserInvite.objects.filter(id=invite_id, invited_by=user).exists():
        raise ValidationError('Приглашение не было создано Вами')


''''' main '''''

def check_can_update_post(user, item):
    check_has_post(user=user, item=item)
    if item.is_closed and item.community_id:
        if not user.is_staff_of_community_with_name(item.community.name):
            raise ValidationError(
                'Вы не можете редактировать закрытую запись',
            )


def check_comments_enabled_for_post_with_id(user, item_id):
    item = Item.objects.select_related('community').get(id=item_id)
    if item.community_id is not None:
        if not user.is_staff_of_community_with_name(item.community.name) and not item.comments_enabled:
            raise ValidationError(
                'Комментарии к этой записи отключены'
            )


def check_can_open_post_with_id(user, item_id):
    item = Item.objects.select_related('community').get(id=item_id)
    if item.community_id is None:
        raise ValidationError(
            'Только сообщения сообщества могут быть открыты / закрыты'
        )

    if not user.is_staff_of_community_with_name(item.community.name):
        raise ValidationError(
            'Только администраторы/модераторы могут открыть эту запись'
        )


def check_can_close_post(user, item):
    if item.community_id is None:
        raise ValidationError(
            'Только сообщения сообщества могут быть открыты / закрыты'
        )

    if not user.is_staff_of_community_with_name(item.community.name):
        raise ValidationError(
            'Только администраторы/модераторы могут закрыть эту запись'
        )


def check_can_delete_post(user, item):

    if not user.has_post(item=item):
        if Item.is_post_with_id_a_community_post(item.pk):
            if not user.is_moderator_of_community_with_name(
                    item.community.name) and not user.is_administrator_of_community_with_name(item.community.name):
                raise ValidationError(
                    'Только модераторы/администраторы могут удалять записи.',
                )
            else:
                item.community.create_remove_post_log(source_user=user,
                                                      target_user=item.creator)
        else:
            raise ValidationError(
                'Вы не можете удалить запись, которое вам не принадлежит'
            )


def check_can_mute_post(user, item):
    if user.has_muted_post_with_id(item_id=item.pk):
        raise ValidationError(
            'Запись уже не отправляет уведомления',
        )
    check_can_see_post(user=user, item=item)


def check_can_unmute_post(user, item):
    check_has_muted_post_with_id(item_id=item.pk, user=user)
    check_can_see_post(user=user, item=item)


def check_has_muted_post_with_id(user, item_id):
    if not user.has_muted_post_with_id(item_id=item_id):
        raise ValidationError(
            'Запись отправляет уведомления',
        )


def check_can_mute_post_comment(user, post_comment):
    if user.has_muted_post_comment_with_id(post_comment_id=post_comment.pk):
        raise ValidationError(
            'Комментарий к записи уже не отправляет уведомления',
        )

    check_can_see_post_comment(user=user, post_comment=post_comment)


def check_can_unmute_post_comment(user, post_comment):
    check_has_muted_post_comment_with_id(user=user, post_comment_id=post_comment.pk)
    check_can_see_post_comment(user=user, post_comment=post_comment)


def check_has_muted_post_comment_with_id(user, post_comment_id):
    if not user.has_muted_post_comment_with_id(post_comment_id=post_comment_id):
        raise ValidationError(
            'Комментарий к записи отправляет уведомления',
        )


def check_has_post(user, item):
    if not user.has_post(item=item):
        raise PermissionDenied(
            'Эта запись не принадлежит вам',
        )


def check_can_edit_comment_with_id_for_post(user, post_comment_id, item):
    check_can_see_post(user=user, item=item)

    if not ItemComment.objects.filter(id=post_comment_id, item_id=item.pk).exists():
        raise ValidationError(
            'Комментарий не относится к указанной записи'
        )

    if item.community and item.is_closed:
        is_administrator = user.is_administrator_of_community_with_name(item.community.name)
        is_moderator = user.is_moderator_of_community_with_name(item.community.name)
        if not is_moderator and not is_administrator:
            raise ValidationError(
                'Только администраторы/модераторы могут редактировать закрытый пост'
            )


def check_has_post_comment_with_id(user, post_comment_id):
    if not user.posts_comments.filter(id=post_comment_id).exists():
        raise ValidationError(
            'Вы не можете редактировать комментарий, который вам не принадлежит'
        )


def check_can_delete_comment_with_id_for_post(user, post_comment_id, item):
    check_can_see_post(user=user, item=item)

    if not ItemComment.objects.filter(id=post_comment_id, item_id=item.pk).exists():
        raise ValidationError(
            'Комментарий не относится к указанной записи'
        )
    is_comment_creator = user.posts_comments.filter(id=post_comment_id).exists()

    if item.community:
        is_moderator = user.is_moderator_of_community_with_name(item.community.name)
        is_administrator = user.is_administrator_of_community_with_name(item.community.name)
        if not is_administrator and not is_moderator:
            if item.is_closed:
                raise ValidationError(
                    'Только модераторы/администраторы могут удалять закрытые записи сообщества',
                )
            elif not is_comment_creator:
                raise ValidationError(
                    'Вы не можете удалить комментарий, который Вам не принадлежит'
                )
        else:
            post_comment = ItemComment.objects.select_related('commenter').get(pk=post_comment_id)
            if post_comment.parent_comment is not None:
                item.community.create_remove_post_comment_reply_log(source_user=user,
                                                                    target_user=post_comment.commenter)
            else:
                item.community.create_remove_post_comment_log(source_user=user,
                                                              target_user=post_comment.commenter)
    elif not item.creator_id == user.pk and not is_comment_creator:
        raise ValidationError(
            'Вы не можете удалить комментарий, который вам не принадлежит'
        )


def check_can_get_comments_for_post(user, item):
    check_can_see_post(user=user, item=item)


def check_can_get_comment_replies_for_post_and_comment(user, item, post_comment):
    if post_comment.item_id != item.id:
        raise ValidationError(
            'Комментарий с заданным идентификатором не найден'
        )
    check_can_see_post(user=user, item=post_comment.item)


def check_can_comment_in_post(user, item):
    check_can_see_post(user=user, item=item)
    check_comments_enabled_for_post_with_id(user=user, item_id=item.id)


def check_can_reply_to_post_comment_for_post(user, post_comment, item):
    if post_comment.item_id != item.id:
        raise ValidationError(
            'Комментарий с заданным идентификатором не найден'
        )

    check_can_comment_in_post(user=user, item=item)


def check_can_see_post(user, item):
    if not user.can_see_post(item):
        raise ValidationError(
            'Эта запись является частной.',
        )


def check_can_see_post_comment(user, post_comment):
    check_can_see_post(user=user, item=post_comment.post)

    if not user.can_see_post_comment(post_comment=post_comment):
        raise ValidationError(
            'Этот комментарий является частным',
        )


def check_can_get_comment_for_post(user, post_comment, item, ):
    check_can_see_post_comment(user=user, post_comment=post_comment)


def check_can_publish_post(user, item):
    check_has_post(user=user, item=item)


def check_can_get_status_for_post(user, item):
    check_has_post(user=user, item=item)


def check_can_get_preview_link_data_for_post(user, item):
    check_can_see_post(item=item, user=user)
    if not item.has_links():
        raise ValidationError(
            'Нет ссылки, связанной с записью.',
        )



""" moderation """

def check_can_report_comment_for_post(user, post_comment, item):
    check_has_not_reported_post_comment_with_id(user=user, post_comment_id=post_comment.pk)
    check_can_see_post(user=user, item=item)

    if post_comment.commenter_id == user.pk:
        raise ValidationError(
            'Вы не можете создать репорт собственного комментария',
        )


def check_has_not_reported_post_comment_with_id(user, post_comment_id):
    if user.has_reported_post_comment_with_id(post_comment_id=post_comment_id):
        raise ValidationError(
            'Вы уже создали репорт о комментарии.',
        )


def check_can_report_post(user, item):
    check_can_see_post(user=user, item=item)
    check_has_not_reported_post_with_id(user=user, item_id=item.pk)
    if item.creator_id == user.pk:
        raise ValidationError(
            'Вы не можете создать репорт собственного сообщения',
        )


def check_has_not_reported_post_with_id(user, item_id):
    if user.has_reported_post_with_id(item_id=item_id):
        raise ValidationError(
            'Вы уже создали репорт о записи.',
        )


def check_can_report_user(user, user_to_report):
    check_has_not_reported_user_with_id(user=user, user_id=user_to_report.pk)
    if user.pk == user_to_report.pk:
        raise ValidationError(
            'Вы не можете создать репорт о себе...',
        )


def check_has_not_reported_user_with_id(user, user_id):
    if user.has_reported_user_with_id(user_id=user_id):
        raise ValidationError(
            'Вы уже создали репорт об этом пользователе',
        )


def check_can_report_community(user, community):
    check_has_not_reported_community_with_id(user=user, community_id=community.pk)
    if community.creator.pk == user.pk:
        raise ValidationError(
            'Вы не можете создать репорт о своем собственном сообществе',
        )


def check_has_not_reported_community_with_id(user, community_id):
    if user.has_reported_community_with_id(community_id=community_id):
        raise ValidationError(
            'Вы уже сообщили об этом сообществе',
        )


def check_can_get_global_moderated_objects(user):
    check_is_global_moderator(user=user)


def check_can_get_moderated_object(user, moderated_object):
    if user.is_global_moderator():
        return

    check_can_get_community_moderated_objects(user=user, community_name=moderated_object.community)


def check_can_get_community_moderated_objects(user, community_name):
    check_is_staff_of_community_with_name(user=user, community_name=community_name)


def check_has_not_reported_moderated_object_with_id(user, moderated_object_id):
    if user.has_reported_moderated_object_with_id(moderated_object_id=moderated_object_id):
        raise ValidationError(
            'Вы уже сообщили об объекте модерации',
        )


def check_can_update_moderated_object(user, moderated_object):
    check_can_moderate_moderated_object(user=user, moderated_object=moderated_object)

    if moderated_object.is_verified():
        raise PermissionDenied(
            'Модерируемый объект был проверен и больше не может редактироваться.'
        )

    if not moderated_object.is_pending() and not user.is_global_moderator():
        raise PermissionDenied(
            'Модерируемый объект уже утвержден / отклонен.'
        )


def check_can_approve_moderated_object(user, moderated_object):
    check_can_moderate_moderated_object(user=user, moderated_object=moderated_object)

    if moderated_object.is_verified():
        raise ValidationError(
            'Модерируемый объект уже проверен.'
        )


def check_can_reject_moderated_object(user, moderated_object):
    check_can_moderate_moderated_object(user=user, moderated_object=moderated_object)
    if moderated_object.is_verified():
        raise ValidationError(
            'Модерируемый объект уже проверен.'
        )


def check_can_unverify_moderated_object(user, moderated_object):
    check_is_global_moderator(user=user)
    if not moderated_object.is_verified():
        raise ValidationError(
            'Модерируемый объект не был проверен.'
        )


def check_can_verify_moderated_object(user, moderated_object):
    check_is_global_moderator(user=user)
    if moderated_object.is_verified():
        raise ValidationError(
            'Модерируемый объект уже проверен.'
        )

    if moderated_object.is_pending():
        raise ValidationError(
            'Вы не можете проверить управляемый объект со статусом ожидание. Пожалуйста, одобрите или отклоните его.'
        )


def check_can_moderate_moderated_object(user, moderated_object):
    content_object = moderated_object.content_object

    is_global_moderator = user.is_global_moderator()

    if is_global_moderator:
        return

    if isinstance(content_object, Item):
        if content_object.community:
            if not user.is_staff_of_community_with_name(community_name=content_object.community.name):
                raise ValidationError('Только сотрудники сообщества могут модерировать сообщения сообщества')
        else:
            raise ValidationError('Только глобальные модераторы могут модерировать сообщения, не относящиеся к сообществу')
    elif isinstance(content_object, PostComment):
        if content_object.item.community:
            if not user.is_staff_of_community_with_name(community_name=content_object.item.community.name):
                raise ValidationError('Только сотрудники сообщества могут модерировать комментарии к публикациям сообщества')
        else:
            raise ValidationError('Только глобальные модераторы могут модерировать комментарии, не относящиеся к сообществу')
    else:
        raise ValidationError('Не глобальные модераторы могут только модерировать записи и комментарии.')


def check_is_global_moderator(user):
    if not user.is_global_moderator():
        raise PermissionDenied('Не глобальный модератор.')


""" users """

def check_can_get_user_with_id(user, user_id):
    check_is_not_blocked_with_user_with_id(user=user, user_id=user_id)


def check_password_matches(user, password):
    if not user.check_password(password):
        raise AuthenticationFailed(
            'Неправильный пароль',
        )


def check_can_accept_guidelines(user):
    if user.are_guidelines_accepted:
        raise ValidationError('Вы уже приняли правила пользования сайтом трезвый.рус')


def check_can_block_user_with_id(user, user_id):
    if user_id == user.pk:
        raise ValidationError('Вы не можете блокировать себя')
    check_is_not_blocked_with_user_with_id(user=user, user_id=user_id)


def check_can_unblock_user_with_id(user, user_id):
    if not user.has_blocked_user_with_id(user_id=user_id):
        raise ValidationError('Вы не можете разблокировать учетную запись, которую вы не заблокировали')


def check_password_reset_verification_token_is_valid(user, password_verification_token):
    try:
        token_contents = jwt.decode(password_verification_token, settings.SECRET_KEY,
                                    algorithm=settings.JWT_ALGORITHM)

        token_user_id = token_contents['user_id']
        token_type = token_contents['type']

        if token_type != user.JWT_TOKEN_TYPE_PASSWORD_RESET:
            raise ValidationError(
                'Тип токена не соответствует'
            )

        if token_user_id != user.pk:
            raise ValidationError(
                'Идентификатор токена пользователя не совпадает'
            )
        return token_user_id
    except jwt.InvalidSignatureError:
        raise ValidationError(
            'Недопустимая подпись токена'
        )
    except jwt.ExpiredSignatureError:
        raise ValidationError(
            'Срок действия токена истек'
        )
    except jwt.DecodeError:
        raise ValidationError(
            'Не удалось декодировать маркер'
        )
    except KeyError:
        raise ValidationError(
            'Недопустимый токен'
        )


def check_email_verification_token_is_valid_for_email(user, email_verification_token):
    try:
        token_contents = jwt.decode(email_verification_token, settings.SECRET_KEY,
                                    algorithm=settings.JWT_ALGORITHM)
        token_email = token_contents['email']
        new_email = token_contents['new_email']
        token_user_id = token_contents['user_id']
        token_type = token_contents['type']

        if token_type != user.JWT_TOKEN_TYPE_CHANGE_EMAIL:
            raise ValidationError(
                'Тип токена не соответствует'
            )

        if token_email != user.email:
            raise ValidationError(
                'Токен электронной почты не соответствует'
            )

        if token_user_id != user.pk:
            raise ValidationError(
                'Идентификатор пользователя маркера не совпадает'
            )
        return new_email
    except jwt.InvalidSignatureError:
        raise ValidationError(
            'Недопустимая подпись токена'
        )
    except jwt.ExpiredSignatureError:
        raise ValidationError(
            'Срок действия токена истек'
        )
    except jwt.DecodeError:
        raise ValidationError(
            'Не удалось декодировать токен'
        )
    except KeyError:
        raise ValidationError(
            'Недопустимый токен'
        )


def check_email_not_taken(user, email):
    if email == user.email:
        return

    if User.is_email_taken(email=email):
        raise ValidationError(
            'Этот email уже получен.'
        )
