'''
    Membership Application Django Admin
    membership/admin.py
    @author Teerapat Kraisrisirikul (810Teams)
'''


from django.contrib import admin

from community.models import Club, Event, Lab, CommunityEvent
from core.utils import truncate, has_instance
from membership.models import Request, Invitation, Advisory, Membership, CustomMembershipLabel, MembershipLog
from membership.models import ApprovalRequest

import datetime


class RequestAdmin(admin.ModelAdmin):
    ''' Request admin '''
    list_display = ('id', 'user', 'community', 'status', 'created_at', 'updated_at', 'updated_by')
    readonly_fields = ('updated_by',)

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            if obj.status != 'W':
                return ('user', 'community', 'status') + self.readonly_fields
            return ('user', 'community') + self.readonly_fields
        return self.readonly_fields


class InvitationAdmin(admin.ModelAdmin):
    ''' Invitation admin '''
    list_display = ('id', 'community', 'invitor', 'invitee', 'status', 'created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            if obj.status != 'W':
                return ('community', 'invitor', 'invitee', 'status') + self.readonly_fields
            return ('community', 'invitor', 'invitee') + self.readonly_fields
        return self.readonly_fields


class AdvisoryAdmin(admin.ModelAdmin):
    ''' Advisory admin '''
    list_display = ('id', 'advisor', 'community', 'start_date', 'end_date', 'is_active', 'created_at', 'created_by',
                    'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by',)

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('advisor', 'community') + self.readonly_fields
        return self.readonly_fields

    def is_active(self, obj):
        ''' Get active status '''
        return obj.start_date <= datetime.datetime.now().date() <= obj.end_date

    is_active.boolean = True


class CustomMembershipLabelInline(admin.StackedInline):
    ''' Custom membership label inline '''
    model = CustomMembershipLabel
    readonly_fields = ('created_by', 'updated_by',)


class MembershipAdmin(admin.ModelAdmin):
    ''' Membership admin '''
    list_display = ('id', 'user', 'community', 'position', 'position_name', 'is_active', 'status', 'custom_label',
                    'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by',)
    inlines = (CustomMembershipLabelInline,)

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('user', 'community') + self.readonly_fields
        return self.readonly_fields

    def position_name(self, obj):
        ''' Get position name '''
        if has_instance(obj.community, Club):
            return ('Member', 'Staff', 'Vice-President', 'President')[obj.position]
        elif has_instance(obj.community, Event) and not has_instance(obj.community, CommunityEvent):
            return ('Participator', 'Staff', 'Event Co-Creator', 'Event Creator')[obj.position]
        elif has_instance(obj.community, CommunityEvent):
            return ('Participator', 'Staff', 'Vice-President', 'President')[obj.position]
        elif has_instance(obj.community, Lab):
            return ('Lab Member', 'Lab Helper', 'Lab Co-Supervisor', 'Lab Supervisor')[obj.position]


    def is_active(self, obj):
        ''' Get active status '''
        return obj.status == 'A'

    is_active.boolean = True

    def custom_label(self, obj):
        ''' Get custom label '''
        return CustomMembershipLabel.objects.get(membership_id=obj.id).label


class MembershipLogAdmin(admin.ModelAdmin):
    ''' Membership log admin '''
    list_display = ('id', 'membership', 'position', 'status', 'start_datetime', 'end_datetime', 'created_by',
                    'updated_by')
    readonly_fields = ('start_datetime', 'end_datetime', 'created_by', 'updated_by',)


class ApprovalRequestAdmin(admin.ModelAdmin):
    ''' Approval request admin '''
    list_display = ('id', 'community', 'partial_message', 'has_attached_file', 'status', 'created_at', 'created_by',
                    'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by',)

    def partial_message(self, obj):
        ''' Get partial message '''
        return truncate(obj.message, max_length=32)

    def has_attached_file(self, obj):
        ''' Get attached file status '''
        return obj.attached_file is not None and obj.attached_file != ''

    has_attached_file.boolean = True


admin.site.register(Request, RequestAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Advisory, AdvisoryAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(MembershipLog, MembershipLogAdmin)
admin.site.register(ApprovalRequest, ApprovalRequestAdmin)
