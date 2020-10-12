from django.core.mail import send_mail
from django.utils.translation import gettext as _

from asset.models import Announcement
from clubs_and_events.settings import EMAIL_HOST_USER
from community.models import CommunityEvent, Event
from core.utils import get_email
from membership.models import Request, MembershipLog
from notification.models import RequestNotification, MembershipLogNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification
from user.models import EmailPreference


class InvalidNotificationType(Exception):
    pass


def notify(users=tuple(), obj=None, mail=False):
    for i in users:
        if isinstance(obj, Request):
            RequestNotification.objects.create(user_id=i.id, request_id=obj.id)
        elif isinstance(obj, MembershipLog):
            MembershipLogNotification.objects.create(user_id=i.id, membership_log=obj.id)
        elif isinstance(obj, Announcement):
            AnnouncementNotification.objects.create(user_id=i.id, announcement_id=obj.id)
        elif isinstance(obj, CommunityEvent):
            CommunityEventNotification.objects.create(user_id=i.id, community_event_id=obj.id)
        elif isinstance(obj, Event):
            EventNotification.objects.create(user_id=i.id, event_id=obj.id)
        else:
            raise InvalidNotificationType

    if mail and obj is not None:
        send_mail_notification(users=users, obj=obj, fail_silently=False)


def send_mail_notification(users=tuple(), obj=None, fail_silently=False):
    email_preferences = EmailPreference.objects.all()
    subject, message, recipients = None, None, None

    if isinstance(obj, Request):
        subject = 'New Join Request in {}'.format(obj.community.name_en)
        message = '{} ({}) has requested to join {}.'.format(
            obj.user.name,
            obj.user.username,
            obj.community.name_en
        )
        recipients = [i for i in users if email_preferences.get(user_id=i.id).receive_request]
    elif isinstance(obj, MembershipLog):
        return
    elif isinstance(obj, Announcement):
        subject = 'New Announcement in {}'.format(obj.community.name_en)
        message = '{} has created a new announcement in {}.\n"{}".'.format(
            obj.created_by,
            obj.community.name_en,
            obj.text
        )
        recipients = [i for i in users if email_preferences.get(user_id=i.id).receive_announcement]
    elif isinstance(obj, CommunityEvent):
        subject = 'New Community Event in {}'.format(obj.name_en)
        message = '{} has created a new community event in {}. The event will be held on {}~{} from {} to {}.'.format(
            obj.created_by.name,
            obj.created_under.name_en,
            obj.start_time,
            obj.end_date,
            obj.start_date,
            obj.end_date
        )
        recipients = [i for i in users if email_preferences.get(user_id=i.id).receive_community_event]
    elif isinstance(obj, Event):
        subject = 'New Event: {}'
        message = '{} has created a new event {}. The event will be held on {}~{} from {} to {}.'.format(
            obj.created_by,
            obj.name_en,
            obj.start_time,
            obj.end_date,
            obj.start_date,
            obj.end_date
        )
        recipients = [i for i in users if email_preferences.get(user_id=i.id).receive_event]

    if subject is not None and message is not None and recipients is not None:
        send_mail(
            _(subject),
            _(message),
            EMAIL_HOST_USER,
            [get_email(i) for i in recipients],
            fail_silently=fail_silently,
        )
