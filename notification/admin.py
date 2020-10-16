from django.contrib import admin

from notification.models import Notification, RequestNotification, MembershipLogNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_read', 'notification_type', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('user',) + self.readonly_fields
        return self.readonly_fields

    def has_add_permission(self, request):
        return False

    def notification_type(self, obj):
        try:
            RequestNotification.objects.get(pk=obj.id)
            return 'Request'
        except RequestNotification.DoesNotExist:
            pass

        try:
            MembershipLogNotification.objects.get(pk=obj.id)
            return 'Membership Log'
        except MembershipLogNotification.DoesNotExist:
            pass

        try:
            AnnouncementNotification.objects.get(pk=obj.id)
            return 'Announcement'
        except AnnouncementNotification.DoesNotExist:
            pass

        try:
            CommunityEventNotification.objects.get(pk=obj.id)
            return 'Community Event'
        except CommunityEventNotification.DoesNotExist:
            pass

        try:
            EventNotification.objects.get(pk=obj.id)
            return 'Event'
        except EventNotification.DoesNotExist:
            pass

        return None


class RequestNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'request', 'is_read', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('user', 'request') + self.readonly_fields
        return self.readonly_fields


class MembershipLogNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_log', 'is_read', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('user', 'membership_log') + self.readonly_fields
        return self.readonly_fields


class AnnouncementNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'announcement', 'is_read', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('user', 'announcement') + self.readonly_fields
        return self.readonly_fields


class CommunityEventNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'community_event', 'is_read', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('user', 'community_event') + self.readonly_fields
        return self.readonly_fields


class EventNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'is_read', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('user', 'event') + self.readonly_fields
        return self.readonly_fields


admin.site.register(Notification, NotificationAdmin)
admin.site.register(RequestNotification, RequestNotificationAdmin)
admin.site.register(MembershipLogNotification, MembershipLogNotificationAdmin)
admin.site.register(AnnouncementNotification, AnnouncementNotificationAdmin)
admin.site.register(CommunityEventNotification, CommunityEventNotificationAdmin)
admin.site.register(EventNotification, EventNotificationAdmin)
