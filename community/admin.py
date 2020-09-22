from django.contrib import admin
from django.contrib.auth.models import Permission

from community.models import Club, Event, CommunityEvent, Lab
from membership.models import Membership


class MembershipInline(admin.StackedInline):
    model = Membership
    extra = 1


class ClubAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible',
                    'club_type', 'room', 'founded_date', 'is_official', 'status']
    inlines = [MembershipInline]


class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible',
                    'event_type', 'event_series', 'start_date', 'end_date', 'status', 'is_community_event']
    inlines = [MembershipInline]

    def is_community_event(self, obj):
        return CommunityEvent.objects.get(pk=obj.id) != None

    is_community_event.boolean = True


class CommunityEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible',
                    'event_type', 'event_series', 'start_date', 'end_date', 'status',
                    'created_under', 'allows_outside_participators']
    inlines = [MembershipInline]


class LabAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible',
                    'room', 'founded_date', 'tags', 'status']
    inlines = [MembershipInline]


admin.site.register(Permission)
admin.site.register(Club, ClubAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(CommunityEvent, CommunityEventAdmin)
admin.site.register(Lab, LabAdmin)
