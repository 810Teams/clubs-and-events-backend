'''
    Community Application Django Admin
    community/admin.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib import admin

from community.models import Club, Event, CommunityEvent, Lab
from core.utils.general import has_instance
from membership.models import Membership, Advisory, Invitation, Request, ApprovalRequest


class MembershipInline(admin.TabularInline):
    ''' Membership inline '''
    readonly_fields = ('created_by', 'updated_by')
    model = Membership
    extra = 1


class InvitationInline(admin.TabularInline):
    ''' Invitation inline '''
    model = Invitation
    extra = 0


class RequestInline(admin.TabularInline):
    ''' Request inline '''
    readonly_fields = ('updated_by',)
    model = Request
    extra = 0


class AdvisoryInline(admin.TabularInline):
    ''' Advisory inline '''
    readonly_fields = ('created_by', 'updated_by')
    model = Advisory
    extra = 0


class ApprovalRequestInline(admin.TabularInline):
    ''' Approval request inline '''
    readonly_fields = ('created_by', 'updated_by')
    model = ApprovalRequest
    extra = 0


class ClubAdmin(admin.ModelAdmin):
    ''' Club admin '''
    list_display = ('id', 'name_th', 'name_en', 'is_publicly_visible', 'is_accepting_requests', 'club_type', 'room',
                    'is_official', 'status', 'valid_through', 'is_active', 'created_at', 'updated_at')
    readonly_fields = ('created_by', 'updated_by')
    inlines = (MembershipInline, InvitationInline, RequestInline, AdvisoryInline, ApprovalRequestInline)
    list_per_page = 20


class EventAdmin(admin.ModelAdmin):
    ''' Event admin '''
    list_display = ('id', 'name_th', 'name_en', 'is_publicly_visible', 'is_accepting_requests', 'event_type',
                    'start_date', 'end_date', 'is_approved', 'is_cancelled', 'is_community_event', 'is_active',
                    'created_at', 'updated_at',)
    readonly_fields = ('created_by', 'updated_by')
    inlines = (MembershipInline, InvitationInline, RequestInline, AdvisoryInline, ApprovalRequestInline)
    list_per_page = 20

    def is_community_event(self, obj):
        ''' Return true if the event is a community event '''
        if has_instance(obj, CommunityEvent):
            return True
        return False

    is_community_event.boolean = True


class CommunityEventAdmin(admin.ModelAdmin):
    ''' Community event admin '''
    list_display = ('id', 'name_th', 'name_en', 'is_publicly_visible', 'is_accepting_requests', 'event_type',
                    'event_series', 'start_date', 'end_date', 'is_approved', 'is_cancelled', 'created_under',
                    'allows_outside_participators', 'is_active', 'created_at', 'updated_at')
    readonly_fields = ('created_by', 'updated_by')
    inlines = (MembershipInline, InvitationInline, RequestInline)
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('created_under',) + self.readonly_fields
        return self.readonly_fields


class LabAdmin(admin.ModelAdmin):
    ''' Lab admin '''
    list_display = ('id', 'name_th', 'name_en', 'is_publicly_visible', 'is_accepting_requests', 'room', 'main_tags',
                    'status', 'is_active', 'created_at', 'updated_at')
    readonly_fields = ('created_by', 'updated_by')
    inlines = (MembershipInline, InvitationInline, RequestInline)
    list_per_page = 20

    def main_tags(self, obj):
        ''' Get two first tags '''
        try:
            tags = [i.strip() for i in obj.tags.split(',')]
            return ', '.join(tags[0:2]) + ', ...' * (len(tags) > 2)
        except (AttributeError, IndexError):
            return None


admin.site.register(Club, ClubAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(CommunityEvent, CommunityEventAdmin)
admin.site.register(Lab, LabAdmin)
