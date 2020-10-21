from rest_framework import serializers

from core.utils import has_instance
from notification.models import Notification, RequestNotification, MembershipLogNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification


class NotificationSerializer(serializers.ModelSerializer):
    meta = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('user', 'created_by', 'updated_by')

    def get_meta(self, obj):
        notification_type = None
        community_id = None

        if has_instance(obj, RequestNotification):
            notification_type = 'request'
            community_id = RequestNotification.objects.get(pk=obj.id).request.community.id
        elif has_instance(obj, MembershipLogNotification):
            notification_type = 'membership_log'
            community_id = MembershipLogNotification.objects.get(pk=obj.id).membership.community.id
        elif has_instance(obj, AnnouncementNotification):
            notification_type = 'announcement'
            community_id = AnnouncementNotification.objects.get(pk=obj.id).announcement.community.id
        elif has_instance(obj, CommunityEventNotification):
            notification_type = 'community_event'
            community_id = CommunityEventNotification.objects.get(pk=obj.id).community_event.id
        elif has_instance(obj, EventNotification):
            notification_type = 'event'
            community_id = EventNotification.objects.get(pk=obj.id).event.id

        return {'notification_type': notification_type, 'community_id': community_id}


class RequestNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestNotification
        fields = '__all__'
        read_only_fields = ('user', 'request', 'created_by', 'updated_by')


class MembershipLogNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipLogNotification
        fields = '__all__'
        read_only_fields = ('user', 'membership_log', 'created_by', 'updated_by')


class AnnouncementNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementNotification
        fields = '__all__'
        read_only_fields = ('user', 'announcement', 'created_by', 'updated_by')


class CommunityEventNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityEventNotification
        fields = '__all__'
        read_only_fields = ('user', 'community_event', 'created_by', 'updated_by')


class EventNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventNotification
        fields = '__all__'
        read_only_fields = ('user', 'event', 'created_by', 'updated_by')
