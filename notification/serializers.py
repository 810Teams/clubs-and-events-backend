'''
    Notification Application Serializers
    notification/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import serializers

from core.utils import has_instance
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

        if has_instance(obj, RequestNotification):
            notification_type = 'request'
            object_id = RequestNotification.objects.get(pk=obj.id).request.id
            community_id = RequestNotification.objects.get(pk=obj.id).request.community.id
        elif has_instance(obj, MembershipLogNotification):
            notification_type = 'membership_log'
            object_id = MembershipLogNotification.objects.get(pk=obj.id).membership_log.id
            community_id = MembershipLogNotification.objects.get(pk=obj.id).membership_log.membership.community.id
        elif has_instance(obj, AnnouncementNotification):
            notification_type = 'announcement'
            object_id = AnnouncementNotification.objects.get(pk=obj.id).announcement.id
            community_id = AnnouncementNotification.objects.get(pk=obj.id).announcement.community.id
        elif has_instance(obj, CommunityEventNotification):
            notification_type = 'community_event'
            object_id = CommunityEventNotification.objects.get(pk=obj.id).community_event.id
            community_id = CommunityEventNotification.objects.get(pk=obj.id).community_event.id
        elif has_instance(obj, EventNotification):
            notification_type = 'event'
            object_id = EventNotification.objects.get(pk=obj.id).event.id
            community_id = EventNotification.objects.get(pk=obj.id).event.id

        return {'notification_type': notification_type, 'object_id': object_id, 'community_id': community_id}


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
