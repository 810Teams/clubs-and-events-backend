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
from clubs_and_events.settings import EMAIL_HOST_USER, EMAIL_NOTIFICATIONS, SEND_IMAGES_AS_ATTACHMENTS, FRONT_END_URL
from community.models import CommunityEvent, Event
from core.utils.users import get_email
from core.utils.filters import get_previous_membership_log, get_latest_membership_log
from membership.models import Request, MembershipLog, Membership, Invitation
from notification.models import RequestNotification, MembershipLogNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification
from user.models import EmailPreference

import socket
import threading


class InvalidNotificationType(Exception):
    ''' Invalid notification type exception '''
    pass


def notify(users=tuple(), obj=None):
    ''' Send notification to manually designated users based on the object  '''
    # Valid notification type verification and notification creation
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
        elif isinstance(obj, Invitation):
            pass
        else:
            raise InvalidNotificationType

    # Verify sending email notifications allowance
    if isinstance(obj, (Request, Announcement, CommunityEvent, Event, Invitation)):
        mail = EMAIL_NOTIFICATIONS
    else:
        mail = False

    # Send email notifications
    if mail and len(users) > 0:
        send_mail_notification(
            users=[i for i in users if EmailPreference.objects.get(user_id=i.id).email_language == 'en'],
            obj=obj, lang='en', fail_silently=False
        )
        send_mail_notification(
            users=[i for i in users if EmailPreference.objects.get(user_id=i.id).email_language == 'th'],
            obj=obj, lang='th', fail_silently=False
        )


def notify_membership_log(obj):
    ''' Send notification to automatically designated users based on the membership log object '''
    if isinstance(obj, Membership):
        obj = get_latest_membership_log(obj)
    elif obj is None or not isinstance(obj, MembershipLog):
        return

    previous_log = get_previous_membership_log(obj)

    if get_current_user().id != obj.membership.user.id:
        # You get promoted or demoted
        if previous_log is not None and previous_log.position != obj.position and previous_log.status == obj.status:
            notify(users=(obj.membership.user,), obj=obj)

        # You get removed
        elif previous_log is not None and previous_log.status != obj.status and obj.status == 'X':
            notify(users=(obj.membership.user,), obj=obj)

        # Someone joined
        elif (previous_log is None or previous_log.status in ('L', 'X')) and obj.status == 'A':
            memberships = Membership.objects.filter(community_id=obj.membership.community.id, status='A')
            memberships = memberships.exclude(user_id=obj.membership.user.id)
            notify(users=tuple([i.user for i in memberships]), obj=obj)


def send_mail_notification(users=tuple(), obj=None, lang='en', fail_silently=False):
    ''' Send email notifications script (function) '''
    thread = threading.Thread(target=send_mail_notification_process, args=[users, obj, lang, fail_silently])
    thread.start()


def send_mail_notification_process(users=tuple(), obj=None, lang='en', fail_silently=False):
    ''' Send email notifications script (process) '''
    # Initialization
    email_preferences = EmailPreference.objects.all()
    subject, title, message = str(), str(), str()
    recipients, attachments = list(), list()

    # Email Content
    # Request Notification
    if isinstance(obj, Request):
        # New request
        if obj.status == 'W':
            if lang == 'en':
                subject = 'New join request: {}'.format(obj.community.name_en)
                title = 'New Join Request in {}'.format(obj.community.name_en)
                message = '{} ({}) has requested to join <b>{}</b>. Sign in and visit the requests tab of the ' + \
                          'community page to respond to this request.'
                message = message.format(
                    obj.user.name,
                    obj.user.username,
                    obj.community.name_en
                )
            elif lang == 'th':
                subject = 'คำขอเข้าร่วมใหม่: {}'.format(obj.community.name_th)
                title = 'คำขอเข้าร่วมใหม่: {}'.format(obj.community.name_th)
                message = '{} ({}) ได้ส่งคำขอเข้าร่วม <b>{}</b> คุณสามารถเข้าสู่ระบบและไปยังแท็บคำขอเข้าร่วมเพื่อตอบรับคำขอเข้าร่วมดังกล่าวได้'
                message = message.format(
                    obj.user.name,
                    obj.user.username,
                    obj.community.name_th
                )
        # Accepted request
        elif obj.status == 'A':
            if lang == 'en':
                subject = 'Join request accepted: {}'.format(obj.community.name_en)
                title = 'Join Request Accepted: {}'.format(obj.community.name_en)
                message = 'Your request to join <b>{}</b> sent on {} is accepted by {}. You can now view all ' + \
                          'community-private content by signing in and visit the community page.'
                message = message.format(
                    obj.community.name_en,
                    obj.created_at,
                    obj.updated_by.name
                )
            elif lang == 'th':
                subject = 'คำขอเข้าร่วมถูกตอบรับ: {}'.format(obj.community.name_th)
                title = 'คำขอเข้าร่วมถูกตอบรับ: {}'.format(obj.community.name_th)
                message = 'คำขอเข้าร่วมของคุณสู่ <b>{}</b> ที่ได้ส่งเมื่อ {} ถูกตอบรับโดย {} คุณสามารถดูเนื้อหาภายในชุมชนได้โดยเข้าสู่ระบบและ' + \
                          'เยี่ยมชมหน้าชุมชนนั้น ๆ'
                message = message.format(
                    obj.community.name_th,
                    obj.created_at,
                    obj.updated_by.name
                )
        # Declined request, should never occur
        else:
            raise InvalidNotificationType

        recipients = [i for i in users if email_preferences.get(user_id=i.id).receive_request]

    # Announcement Notification
    elif isinstance(obj, Announcement):
        if lang == 'en':
            subject = 'New announcement: {}'.format(obj.community.name_en)
            title = 'New Announcement in {}'.format(obj.community.name_en)
            message = 'A new announcement is created in {}. The announcement message is as follows.<br><br>{}'
            message = message.format(
                obj.community.name_en,
                obj.text
            )
        elif lang == 'th':
            subject = 'ประกาศใหม่: {}'.format(obj.community.name_th)
            title = 'ประกาศใหม่: {}'.format(obj.community.name_th)
            message = 'ประกาศใหม่ได้ถูกสร้างใน {} ข้อความของประกาศเป็นดังนี้.<br><br>{}'
            message = message.format(
                obj.community.name_th,
                obj.text
            )

        recipients = [i for i in users if email_preferences.get(user_id=i.id).receive_announcement]

        try:
            attachments.append(obj.image.url)
        except ValueError:
            pass

    # Community Event Notification
    elif isinstance(obj, CommunityEvent):
        if lang == 'en':
            subject = 'New community event: {}'.format(obj.name_en)
            title = 'New Community Event: {}'.format(obj.name_en)
            message = 'A new event <b>{}</b> from {} is created! The event will take place on {} to {} during {} ' + \
                      'to {}. Apply yourself as a participator by signing in and send a join request to this event.'
            message = message.format(
                obj.name_en,
                obj.created_under.name_en,
                obj.start_time,
                obj.end_time,
                obj.start_date,
                obj.end_date
            )
        elif lang == 'th':
            subject = 'กิจกรรมใหม่: {}'.format(obj.name_th)
            title = 'กิจกรรมใหม่: {}'.format(obj.name_th)
            message = 'กิจกรรมใหม่ <b>{}</b> จาก {} จะถูกจัดขึ้น! กิจกรรมจะจัดขึ้นในวันที่ {} ถึง {} เป็นเวลาตั้งแต่ {} ถึงเวลา {} ' + \
                      'คุณสามารถเข้าร่วมได้โดยการเข้าสู่ระบบและส่งคำขอเข้าร่วมกิจกรรมดังกล่าวได้'
            message = message.format(
                obj.name_th,
                obj.created_under.name_th,
                obj.start_time,
                obj.end_time,
                obj.start_date,
                obj.end_date
            )

        recipients = [i for i in users if email_preferences.get(user_id=i.id).receive_community_event]

    # Event Notification
    elif isinstance(obj, Event) and not isinstance(obj, CommunityEvent):
        if lang == 'en':
            subject = 'New event: {}'.format(obj.name_en)
            title = 'New Event: {}'.format(obj.name_en)
            message = 'A new event <b>{}</b> is announced! The event will take place on {} to {} during {} to {}.' + \
                      'Apply yourself as a participator by signing in and send a join request to this event.'
            message = message.format(
                obj.name_en,
                obj.start_time,
                obj.end_time,
                obj.start_date,
                obj.end_date
            )
        elif lang == 'th':
            subject = 'กิจกรรมใหม่: {}'.format(obj.name_th)
            title = 'กิจกรรมใหม่: {}'.format(obj.name_th)
            message = 'กิจกรรมใหม่ <b>{}</b> จะถูกจัดขึ้น! กิจกรรมจะจัดขึ้นในวันที่ {} ถึง {} เป็นเวลาตั้งแต่ {} ถึงเวลา {} ' + \
                      'คุณสามารถเข้าร่วมได้โดยการเข้าสู่ระบบและส่งคำขอเข้าร่วมกิจกรรมดังกล่าวได้'
            message = message.format(
                obj.name_th,
                obj.start_time,
                obj.end_time,
                obj.start_date,
                obj.end_date
            )

        recipients = [i for i in users if email_preferences.get(user_id=i.id).receive_event]

    # Invitation Notification
    elif isinstance(obj, Invitation):
        if lang == 'en':
            subject = 'New invitation: {}'.format(obj.community.name_en)
            title = 'New Invitation: {}'.format(obj.community.name_en)
            message = '<b>{}</b> has invited you to join <b>{}</b>. Sign in to respond to this invitation.'
            message = message.format(
                obj.invitor.name,
                obj.community.name_en
            )
        elif lang == 'th':
            subject = 'คำเชิญใหม่: {}'.format(obj.community.name_th)
            title = 'คำเชิญใหม่: {}'.format(obj.community.name_th)
            message = '<b>{}</b> ได้ส่งคำเชิญให้คุณเพื่อเข้าร่วม <b>{}</b> เข้าสู่ระบบเพื่อตอบรับคำเชิญนี้'
            message = message.format(
                obj.invitor.name,
                obj.community.name_th
            )

        recipients = [i for i in users if email_preferences.get(user_id=i.id).receive_invitation]

    # Invalid Notification Type
    else:
        raise InvalidNotificationType

    # Email Delivery
    for i in recipients:
        # Email object
        email = EmailMultiAlternatives(_(subject), _(message), EMAIL_HOST_USER, [get_email(i)])

        # Replacing email template with contents
        html_content = str().join(list(open('notification/templates/mail-{}.html'.format(lang), encoding='utf-8')))
        html_content = html_content.replace('{title}', title)
        html_content = html_content.replace('{message}', message)
        html_content = html_content.replace(
            '{unsubscribe_url}',
            'https://{}/unsubscribe/?username={}key={}'.format(
                FRONT_END_URL,
                EmailPreference.objects.get(user_id=i.id).user.username,
                EmailPreference.objects.get(user_id=i.id).unsubscribe_key
            )
        )

        # Images
        if SEND_IMAGES_AS_ATTACHMENTS:
            for j in attachments:
                with open(j, mode='rb') as f:
                    image = MIMEImage(f.read())
                    email.attach(image)
            html_content = html_content.replace('{images}', str())
        else:
            html_image_component = str().join(list(open('notification/templates/image.html')))
            html_image_content = '\n'.join([
                html_image_component.replace(
                    '{path}', 'http://{}:8000{}'.format(socket.gethostbyname(socket.gethostname()), j)
                ) for j in attachments
            ])
            html_content = html_content.replace('{images}', html_image_content)

        # Send
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=fail_silently)
