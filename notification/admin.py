'''
    Notification Application Django Admin
    notification/admin.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib import admin

from core.utils import has_instance
from notification.models import Notification, RequestNotification, MembershipLogNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification


class NotificationAdmin(admin.ModelAdmin):
    ''' Notification admin '''
    list_display = ('user', 'is_read', 'notification_type', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('user',) + self.readonly_fields
        return self.readonly_fields

    def has_add_permission(self, request):
        ''' Restricts add permission '''
        return False

    def notification_type(self, obj):
        ''' Get notification type '''
        if has_instance(obj, RequestNotification):
            return 'Request'
        elif has_instance(obj, MembershipLogNotification.objects):
            return 'Membership Log'
        elif has_instance(obj, AnnouncementNotification):
            return 'Announcement'
        elif has_instance(obj, CommunityEventNotification):
            return 'Community Event'
        elif has_instance(obj, EventNotification.objects):
            return 'Event'
        return None


class RequestNotificationAdmin(admin.ModelAdmin):
    ''' Request notification admin '''
    list_display = ('user', 'request', 'is_read', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('user', 'request') + self.readonly_fields
        return self.readonly_fields


class MembershipLogNotificationAdmin(admin.ModelAdmin):
    ''' Membership log notification admin '''
    list_display = ('user', 'membership_log', 'is_read', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('user', 'membership_log') + self.readonly_fields
        return self.readonly_fields


class AnnouncementNotificationAdmin(admin.ModelAdmin):
    ''' Announcement notification admin '''
    list_display = ('user', 'announcement', 'is_read', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('user', 'announcement') + self.readonly_fields
        return self.readonly_fields


class CommunityEventNotificationAdmin(admin.ModelAdmin):
    ''' Community event notification admin '''
    list_display = ('user', 'community_event', 'is_read', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('user', 'community_event') + self.readonly_fields
        return self.readonly_fields


class EventNotificationAdmin(admin.ModelAdmin):
    ''' Event notification admin '''
    list_display = ('user', 'event', 'is_read', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('user', 'event') + self.readonly_fields
        return self.readonly_fields


admin.site.register(Notification, NotificationAdmin)
admin.site.register(RequestNotification, RequestNotificationAdmin)
admin.site.register(MembershipLogNotification, MembershipLogNotificationAdmin)
admin.site.register(AnnouncementNotification, AnnouncementNotificationAdmin)
admin.site.register(CommunityEventNotification, CommunityEventNotificationAdmin)
admin.site.register(EventNotification, EventNotificationAdmin)
