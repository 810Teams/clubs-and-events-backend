from django.contrib import admin
from django.utils.translation import gettext as _

from community.models import Club, Event, CommunityEvent, Lab
from membership.models import Membership, Advisory, Invitation, Request


class MembershipInline(admin.TabularInline):
    readonly_fields = ('created_by', 'updated_by')
    model = Membership
    extra = 1


class InvitationInline(admin.TabularInline):
    model = Invitation
    extra = 0


class RequestInline(admin.TabularInline):
    readonly_fields = ('updated_by',)
    model = Request
    extra = 0


class AdvisoryInline(admin.TabularInline):
    readonly_fields = ('created_by', 'updated_by')
    model = Advisory
    extra = 0


class ClubAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible', 'is_accepting_requests', 'created_at',
                    'updated_at', 'club_type', 'room', 'founded_date', 'is_official', 'status')
    readonly_fields = ('created_by', 'updated_by')
    inlines = (MembershipInline, InvitationInline, RequestInline, AdvisoryInline)


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible', 'is_accepting_requests', 'created_at',
                    'updated_at', 'event_type', 'event_series', 'start_date', 'end_date', 'is_approved', 'is_cancelled',
                    'is_community_event')
    readonly_fields = ('created_by', 'updated_by')
    inlines = (MembershipInline, InvitationInline, RequestInline, AdvisoryInline)

    def is_community_event(self, obj):
        try:
            if CommunityEvent.objects.get(pk=obj.id):
                return True
        except CommunityEvent.DoesNotExist:
            return False

    is_community_event.boolean = True


class CommunityEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible', 'is_accepting_requests', 'created_at',
                    'updated_at','event_type', 'event_series', 'start_date', 'end_date', 'is_approved', 'is_cancelled',
                    'created_under', 'allows_outside_participators')
    readonly_fields = ('created_by', 'updated_by')
    inlines = (MembershipInline, InvitationInline, RequestInline)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('created_under',) + self.readonly_fields
        return self.readonly_fields


class LabAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible', 'is_accepting_requests', 'created_at',
                    'updated_at', 'room', 'founded_date', 'tags', 'status')
    readonly_fields = ('created_by', 'updated_by')
    inlines = (MembershipInline, InvitationInline, RequestInline)


admin.site.register(Club, ClubAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(CommunityEvent, CommunityEventAdmin)
admin.site.register(Lab, LabAdmin)
