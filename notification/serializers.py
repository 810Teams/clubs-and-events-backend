from rest_framework import serializers

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

        try:
            RequestNotification.objects.get(pk=obj.id)
            notification_type = 'request'
        except RequestNotification.DoesNotExist:
            pass

        try:
            MembershipLogNotification.objects.get(pk=obj.id)
            notification_type = 'membership_log'
        except MembershipLogNotification.DoesNotExist:
            pass

        try:
            AnnouncementNotification.objects.get(pk=obj.id)
            notification_type = 'announcement'
        except AnnouncementNotification.DoesNotExist:
            pass

        try:
            CommunityEventNotification.objects.get(pk=obj.id)
            notification_type = 'community_event'
        except CommunityEventNotification.DoesNotExist:
            pass

        try:
            EventNotification.objects.get(pk=obj.id)
            notification_type = 'event'
        except EventNotification.DoesNotExist:
            pass

        return {'notification_type': notification_type, 'object_id': obj.id}


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
