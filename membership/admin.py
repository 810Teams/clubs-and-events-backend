from django.contrib import admin

from community.models import Club, Event, Lab
from membership.models import Request, Invitation, Advisory, Membership, CustomMembershipLabel

import datetime


class RequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'community', 'status', 'created_at', 'updated_at', 'updated_by']


class InvitationAdmin(admin.ModelAdmin):
    list_display = ['id', 'community', 'invitor', 'invitee', 'status', 'created_at', 'updated_at']


class AdvisoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'advisor', 'community', 'start_date', 'end_date', 'is_active', 'created_at', 'updated_at']

    def is_active(self, obj):
        return obj.start_date <= datetime.datetime.now().date() <= obj.end_date

    is_active.boolean = True


class CustomMembershipLabelInline(admin.StackedInline):
    model = CustomMembershipLabel


class MembershipAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'community', 'position', 'position_name', 'is_active', 'status', 'created_at',
                    'created_by', 'updated_at', 'updated_by']
    inlines = [CustomMembershipLabelInline]

    def position_name(self, obj):
        try:
            if Club.objects.get(pk=obj.community.id) is not None:
                return ('Member', 'Staff', 'Vice-President', 'President')[obj.position]
        except Club.DoesNotExist:
            pass

        try:
            if Event.objects.get(pk=obj.community.id) is not None:
                return ('Participator', 'Staff', 'Vice-President', 'President')[obj.position]
        except Event.DoesNotExist:
            pass

        try:
            if Lab.objects.get(pk=obj.community.id) is not None:
                return ('Lab Member', 'Lab Helper', 'Lab Co-Supervisor', 'Lab Supervisor')[obj.position]
        except Lab.DoesNotExist:
            pass

    def is_active(self, obj):
        return obj.status == 'A'

    is_active.boolean = True


admin.site.register(Request, RequestAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Advisory, AdvisoryAdmin)
admin.site.register(Membership, MembershipAdmin)
