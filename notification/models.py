from crum import get_current_user
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from asset.models import Announcement
from community.models import CommunityEvent, Event
from membership.models import Request, MembershipLog


class Notification(models.Model):
    ''' Base notification '''
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='notification_created_by')


class RequestNotification(Notification):
    ''' Notification when someone requested to join the community '''
    request = models.ForeignKey(Request, on_delete=models.CASCADE)


class JoinNotification(Notification):
    ''' Notification when someone joined the community '''
    membership_log = models.ForeignKey(MembershipLog, on_delete=models.CASCADE)


class RemovedNotification(Notification):
    ''' Notification when you get removed from the community '''
    membership_log = models.ForeignKey(MembershipLog, on_delete=models.CASCADE)


class AnnouncementNotification(Notification):
    ''' Notification when an announcement in the community is made '''
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)


class CommunityEventNotification(Notification):
    ''' Notification when a community event is created in the community '''
    community_event = models.ForeignKey(CommunityEvent, on_delete=models.CASCADE)


class EventNotification(Notification):
    ''' Notification on event promotion '''
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
