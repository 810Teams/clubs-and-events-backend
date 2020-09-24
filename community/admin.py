from django.contrib import admin

from community.models import Club, Event, CommunityEvent, Lab
from membership.models import Membership, Advisory, Invitation, Request


class MembershipInline(admin.StackedInline):
    model = Membership
    extra = 1


class InvitationInline(admin.StackedInline):
    model = Invitation
    extra = 0


class RequestInline(admin.StackedInline):
    model = Request
    extra = 0


class AdvisoryInline(admin.StackedInline):
    model = Advisory
    extra = 0


class ClubAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible', 'created_at',
                    'club_type', 'room', 'founded_date', 'is_official', 'status']
    inlines = [MembershipInline, InvitationInline, RequestInline, AdvisoryInline]


class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible', 'created_at',
                    'event_type', 'event_series', 'start_date', 'end_date', 'is_approved', 'is_cancelled',
                    'is_community_event']
    inlines = [MembershipInline, InvitationInline, RequestInline, AdvisoryInline]

    def is_community_event(self, obj):
        try:
            if CommunityEvent.objects.get(pk=obj.id):
                return True
        except CommunityEvent.DoesNotExist:
            return False

    is_community_event.boolean = True


class CommunityEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible', 'created_at',
                    'event_type', 'event_series', 'start_date', 'end_date', 'is_approved', 'is_cancelled',
                    'created_under', 'allows_outside_participators']
    inlines = [MembershipInline, InvitationInline, RequestInline]


class LabAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible', 'created_at',
                    'room', 'founded_date', 'tags', 'status']
    inlines = [MembershipInline, InvitationInline, RequestInline]


admin.site.register(Club, ClubAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(CommunityEvent, CommunityEventAdmin)
admin.site.register(Lab, LabAdmin)
