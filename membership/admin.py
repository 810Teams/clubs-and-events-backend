from django.contrib import admin

from membership.models import Request, Invitation, Advisory, Membership, CustomMembershipLabel

import datetime


class RequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'community', 'status', 'created_at', 'updated_at', 'updated_by']


class InvitationAdmin(admin.ModelAdmin):
    list_display = ['id', 'community', 'invitor', 'invitee', 'invited_datetime', 'status', 'created_at', 'updated_at']


class AdvisoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'advisor', 'community', 'start_date', 'end_date', 'is_active', 'created_at', 'updated_at']

    def is_active(self, obj):
        return obj.start_date <= datetime.datetime.now().date() <= obj.end_date

    is_active.boolean = True


class CustomMembershipLabelInline(admin.StackedInline):
    model = CustomMembershipLabel


class MembershipAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'community', 'position', 'is_active', 'status', 'created_at', 'updated_at',
                    'updated_by']
    inlines = [CustomMembershipLabelInline]

    def is_active(self, obj):
        return obj.status == 'A'

    is_active.boolean = True


admin.site.register(Request, RequestAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Advisory, AdvisoryAdmin)
admin.site.register(Membership, MembershipAdmin)
