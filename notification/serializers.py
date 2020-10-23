'''
    Notification Application Serializers
    notification/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.utils.translation import gettext as _
from rest_framework import serializers

from core.utils import has_instance
from membership.serializers import MembershipLogSerializer
from notification.models import Notification, RequestNotification, MembershipLogNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification


class NotificationSerializer(serializers.ModelSerializer):
    ''' Notification serializer '''
    meta = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = Notification
        fields = '__all__'
        read_only_fields = ('user', 'created_by', 'updated_by')

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        notification_type = None
        object_id = None
        community_id = None
        text = ''

        if has_instance(obj, RequestNotification):
            notification = RequestNotification.objects.get(pk=obj.id)
            notification_type = 'request'
            object_id = notification.request.id
            community_id = notification.request.community.id

            if self.context['request'].user.id != notification.request.user.id:
                text = '{} has requested to join {}.'.format(
                    notification.request.user.name, notification.request.community.name_en
                )
            else:
                text = '{} has accepted your request to join {}.'.format(
                    notification.request.user.name, notification.request.community.name_en
                )
        elif has_instance(obj, MembershipLogNotification):
            notification = MembershipLogNotification.objects.get(pk=obj.id)
            notification_type = 'membership_log'
            object_id = notification.membership_log.id
            community_id = notification.membership_log.membership.community.id
            text = MembershipLogSerializer().get_log_text(notification.membership_log)
        elif has_instance(obj, AnnouncementNotification):
            notification = AnnouncementNotification.objects.get(pk=obj.id)
            notification_type = 'announcement'
            object_id = notification.announcement.id
            community_id = notification.announcement.community.id
            text = 'A new announcement is created in {}.'.format(notification.announcement.community.name_en)
        elif has_instance(obj, CommunityEventNotification):
            notification = CommunityEventNotification.objects.get(pk=obj.id)
            notification_type = 'community_event'
            object_id = notification.community_event.id
            community_id = notification.community_event.id
            text = 'A new event {} is created in {}.'.format(
                notification.community_event.name_en, notification.community_event.created_under.name_en
            )
        elif has_instance(obj, EventNotification):
            notification = EventNotification.objects.get(pk=obj.id)
            notification_type = 'event'
            object_id = notification.event.id
            community_id = notification.event.id
            text = 'A new event {} is created.'.format(notification.event.name_en)

        return {
            'notification_type': notification_type,
            'object_id': object_id,
            'community_id': community_id,
            'text': _(text)
        }


class RequestNotificationSerializer(serializers.ModelSerializer):
    ''' Request notification serializer '''
    class Meta:
        ''' Meta '''
        model = RequestNotification
        fields = '__all__'
        read_only_fields = ('user', 'request', 'created_by', 'updated_by')


class MembershipLogNotificationSerializer(serializers.ModelSerializer):
    ''' Membership log notification serializer '''
    class Meta:
        ''' Meta '''
        model = MembershipLogNotification
        fields = '__all__'
        read_only_fields = ('user', 'membership_log', 'created_by', 'updated_by')


class AnnouncementNotificationSerializer(serializers.ModelSerializer):
    ''' Announcement notification serializer '''
    class Meta:
        ''' Meta '''
        model = AnnouncementNotification
        fields = '__all__'
        read_only_fields = ('user', 'announcement', 'created_by', 'updated_by')


class CommunityEventNotificationSerializer(serializers.ModelSerializer):
    ''' Community event notification serializer '''
    class Meta:
        ''' Meta '''
        model = CommunityEventNotification
        fields = '__all__'
        read_only_fields = ('user', 'community_event', 'created_by', 'updated_by')


class EventNotificationSerializer(serializers.ModelSerializer):
    ''' Event notification serializer '''
    class Meta:
        ''' Meta '''
        model = EventNotification
        fields = '__all__'
        read_only_fields = ('user', 'event', 'created_by', 'updated_by')
