from django.contrib import admin
from django.contrib.auth.models import Permission

from community.models import *

import datetime


# Initialization

admin.site.register(Permission)


# Group 1 - User
#   - Profile
#   - EmailPreference
#   - StudentCommitteeAuthority

class EmailPreferenceInline(admin.StackedInline):
    model = EmailPreference


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'nickname', 'birthdate', 'last_online', 'is_lecturer']
    inlines = [EmailPreferenceInline]


class StudentCommitteeAuthorityAdmin(admin.ModelAdmin):
    list_display = ['profile', 'start_date', 'end_date', 'is_active']

    def is_active(self, obj):
        return obj.start_date <= datetime.datetime.now().date() <= obj.end_date

    is_active.boolean = True


admin.site.register(Profile, ProfileAdmin)
admin.site.register(StudentCommitteeAuthority, StudentCommitteeAuthorityAdmin)


# Group 2 - Types
#   - ClubType
#   - EventType
#   - EventSeries

class ClubTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'title_th', 'title_en']


class EventTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'title_th', 'title_en']


class EventSeriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'title_th', 'title_en']


admin.site.register(ClubType, ClubTypeAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(EventSeries, EventSeriesAdmin)


# Group 3 - Community
#   - Community
#   - Club
#   - Event
#   - CommunityEvent
#   - Lab

class ClubAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible',
                    'club_type', 'room', 'founded_date', 'is_official', 'status']


class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible',
                    'event_type', 'event_series', 'start_date', 'end_date', 'status', 'is_community_event']

    def is_community_event(self, obj):
        return CommunityEvent.objects.get(pk=obj.id) != None

    is_community_event.boolean = True


class CommunityEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible',
                    'event_type', 'event_series', 'start_date', 'end_date', 'status',
                    'created_under', 'allows_outside_participators']


class LabAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_th', 'name_en', 'url_id', 'is_publicly_visible',
                    'room', 'founded_date', 'tags', 'status']


admin.site.register(Club, ClubAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(CommunityEvent, CommunityEventAdmin)
admin.site.register(Lab, LabAdmin)


# Group 4 - Assets
#   - Announcement
#   - Album
#   - AlbumImage

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['id', 'partial_text', 'created_datetime', 'community', 'creator']

    def partial_text(self, obj):
        if len(obj.text) <= 64:
            return obj.text
        return obj.text[:64] + '...'


class AlbumImageInline(admin.StackedInline):
    model = AlbumImage
    extra = 1


class AlbumAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_datetime', 'community', 'community_event', 'creator']
    inlines = [AlbumImageInline]


class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'partial_text', 'written_by', 'created_by', 'event']

    def partial_text(self, obj):
        if len(obj.text) <= 64:
            return obj.text
        return obj.text[:64] + '...'


admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Comment, CommentAdmin)


# Group 5 - Membership
#   - Request
#   - Invitation
#   - Advisory
#   - Membership
#   - CustomMembershipLabel

class RequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'community', 'status', 'updated_by']


class InvitationAdmin(admin.ModelAdmin):
    list_display = ['id', 'community', 'invitor', 'invitee', 'invited_datetime', 'status']


class AdvisoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'advisor', 'community', 'start_date', 'end_date', 'is_active']

    def is_active(self, obj):
        return obj.start_date <= datetime.datetime.now().date() <= obj.end_date

    is_active.boolean = True


class CustomMembershipLabelInline(admin.StackedInline):
    model = CustomMembershipLabel


class MembershipAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'community', 'position', 'start_date', 'end_date', 'ended_reason', 'is_active']
    inlines = [CustomMembershipLabelInline]

    def is_active(self, obj):
        return obj.end_date == None

    is_active.boolean = True


admin.site.register(Request, RequestAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Advisory, AdvisoryAdmin)
admin.site.register(Membership, MembershipAdmin)
