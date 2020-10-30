'''
    Notification Application Notifier
    notification/notifier.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from crum import get_current_user
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext as _
from email.mime.image import MIMEImage

from asset.models import Announcement
from clubs_and_events.settings import EMAIL_HOST_USER, EMAIL_NOTIFICATIONS
from community.models import CommunityEvent, Event
from core.utils import get_email
from core.filters import get_previous_membership_log
from membership.models import Request, MembershipLog, Membership
from notification.models import RequestNotification, MembershipLogNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification
from user.models import EmailPreference

import threading


class InvalidNotificationType(Exception):
    ''' Invalid notification type exception '''
    pass


def notify(users=tuple(), obj=None):
    ''' Send notification to users function '''
    thread = threading.Thread(target=notify_process, args=[users, obj])
    thread.start()


def notify_process(users=tuple(), obj=None):
    ''' Send notification to users process '''
    for i in users:
        if isinstance(obj, Request):
            RequestNotification.objects.create(user_id=i.id, request_id=obj.id)
        elif isinstance(obj, MembershipLog):
            MembershipLogNotification.objects.create(user_id=i.id, membership_log_id=obj.id)
        elif isinstance(obj, Announcement):
            AnnouncementNotification.objects.create(user_id=i.id, announcement_id=obj.id)
        elif isinstance(obj, CommunityEvent):
            CommunityEventNotification.objects.create(user_id=i.id, community_event_id=obj.id)
        elif isinstance(obj, Event):
            EventNotification.objects.create(user_id=i.id, event_id=obj.id)
        else:
            raise InvalidNotificationType

    if isinstance(obj, (Request, Announcement, CommunityEvent, Event)):
        mail = EMAIL_NOTIFICATIONS
    else:
        mail = False

    # Send email notifications
    if mail and obj is not None:
        send_mail_notification(users=users, obj=obj, fail_silently=False)


def notify_membership_log(obj):
    ''' Send notification regarding membership log to users function '''
    thread = threading.Thread(target=notify_membership_log_process, args=[obj])
    thread.start()


def notify_membership_log_process(obj):
    ''' Send notification regarding membership log to users process '''
    if obj is None or not isinstance(obj, MembershipLog):
        return

    previous_log = get_previous_membership_log(obj)

    if get_current_user().id != obj.membership.user.id:
        # You get promoted or demoted
        if previous_log is not None and previous_log.position != obj.position and previous_log.status == obj.status:
            notify(users=(obj.membership.user,), obj=obj)

        # You get removed
        if previous_log is not None and previous_log.status != obj.status and obj.status == 'X':
            notify(users=(obj.membership.user,), obj=obj)

        # Someone joined
        if (previous_log is None or previous_log.status in ('L', 'X')) and obj.status == 'A':
            memberships = Membership.objects.filter(community_id=obj.membership.community.id, status='A')
            memberships = memberships.exclude(user_id=obj.membership.user.id)
            notify(users=tuple([i.user for i in memberships]), obj=obj)


def send_mail_notification(users=tuple(), obj=None, fail_silently=False):
    ''' Send email notifications script '''
    # Initialization
    email_preferences = EmailPreference.objects.all()
    subject, message, recipients, attachments = None, None, list(), list()

    # Email Content
    if isinstance(obj, Request):
        subject = 'New Join Request in {}'.format(obj.community.name_en)
        message = '{} ({}) has requested to join {}. Sign in and visit the community\'s requests tab to respond ' + \
                  'to this join request.'
        message = message.format(
            obj.user.name,
            obj.user.username,
            obj.community.name_en
        )
        recipients = [i for i in users if email_preferences.get(user_id=i.id).receive_request]
    elif isinstance(obj, Announcement):
        subject = 'New Announcement in {}'.format(obj.community.name_en)
        message = 'A new announcement is created in {}.\n\n"{}"\n\n'
        message = message.format(
            obj.community.name_en,
            obj.text
        )
        recipients = [i for i in users if email_preferences.get(user_id=i.id).receive_announcement]
        attachments = [obj.image.path]
    elif isinstance(obj, CommunityEvent):
        subject = 'New Community Event in {}'.format(obj.name_en)
        message = 'A new event "{}" is from {} is announced! The event will take place on {} to {} during {} to {}.'
        message = message.format(
            obj.name_en,
            obj.created_under.name_en,
            obj.start_date,
            obj.end_date,
            obj.start_time,
            obj.end_date,
        )
        recipients = [i for i in users if email_preferences.get(user_id=i.id).receive_community_event]
    elif isinstance(obj, Event):
        subject = 'New Event: {}'.format(obj.name_en)
        message = 'A new event "{}" is announced! The event will take place on {} to {} during {} to {}.'
        message = message.format(
            obj.name_en,
            obj.start_time,
            obj.end_date,
            obj.start_date,
            obj.end_date
        )
        recipients = [i for i in users if email_preferences.get(user_id=i.id).receive_event]
    else:
        raise InvalidNotificationType
    
    # Email Delivery
    if subject is not None and message is not None and len(recipients) > 0:
        for i in recipients:
            email = EmailMultiAlternatives(_(subject), _(message), EMAIL_HOST_USER, [get_email(i)],)

            for i in attachments:
                with open(i, mode='rb') as f:
                    image = MIMEImage(f.read())
                    email.attach(image)

            # TODO: Implements HTML content, this will entirely replace the original message part.
            # html_content = str()
            # email.attach_alternative(html_content, 'text/html')

            email.send(fail_silently=fail_silently)
