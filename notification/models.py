'''
    Notification Application Models
    notification/models.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from django.db import models

from asset.models import Announcement
from community.models import CommunityEvent, Event
from core.utils.objects import save_user_attributes
from membership.models import Request, MembershipLog


class Notification(models.Model):
    ''' Base notification '''
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='notification_user')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='notification_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='notification_updated_by')

    def __str__(self):
        ''' String representation '''
        return 'Notification Object ({}) [{}]'.format(self.id, self.user.__str__())

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')
        super(Notification, self).save(*args, **kwargs)


class RequestNotification(Notification):
    ''' Notification when someone requested to join the community '''
    request = models.ForeignKey(Request, on_delete=models.CASCADE)

    def __str__(self):
        ''' String representation '''
        return '{} [{}]'.format(self.request.__str__(), self.user.__str__())


class MembershipLogNotification(Notification):
    ''' Notification when someone joined the community or someone removed you from the community '''
    membership_log = models.ForeignKey(MembershipLog, on_delete=models.CASCADE)

    def __str__(self):
        ''' String representation '''
        return '{} [{}]'.format(self.membership_log.__str__(), self.user.__str__())


class AnnouncementNotification(Notification):
    ''' Notification when an announcement in the community is made '''
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)

    def __str__(self):
        ''' String representation '''
        return '{} [{}]'.format(self.announcement.community.__str__(), self.user.__str__())


class CommunityEventNotification(Notification):
    ''' Notification when a community event is created in the community '''
    community_event = models.ForeignKey(CommunityEvent, on_delete=models.CASCADE)

    def __str__(self):
        return '{} [{}]'.format(self.community_event.__str__(), self.user.__str__())


class EventNotification(Notification):
    ''' Notification on event promotion '''
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        ''' String representation '''
        return '{} [{}]'.format(self.event.__str__(), self.user.__str__())
