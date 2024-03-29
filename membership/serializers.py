'''
    Membership Application Serializers
    membership/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from datetime import datetime

from django.utils.translation import gettext as _
from rest_framework import serializers

from clubs_and_events.settings import VOTE_LIMIT_PER_EVENT
from community.models import Community, CommunityEvent, Club, Lab, Event
from community.permissions import IsRenewableClub, IsMemberOfBaseCommunity
from core.permissions import IsDeputyLeaderOfCommunity, IsLeaderOfCommunity, IsMemberOfCommunity, IsInActiveCommunity
from core.utils.filters import get_previous_membership_log
from core.utils.general import has_instance
from core.utils.serializer import add_error_message, validate_profanity_serializer, raise_validation_errors
from core.utils.serializer import field_exists, is_ended_event
from membership.models import Request, Invitation, Membership, CustomMembershipLabel, Advisory, MembershipLog
from membership.models import ApprovalRequest
from membership.permissions import IsAbleToDeleteInvitation
from misc.models import Vote
from user.permissions import IsLecturer, IsLecturerObject, IsStudent, IsStudentObject


class ExistingRequestSerializer(serializers.ModelSerializer):
    ''' Existing request serializer '''
    class Meta:
        ''' Meta '''
        model = Request
        fields = '__all__'
        read_only_fields = ('user', 'community', 'updated_by')

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        if data['status'] == 'W':
            add_error_message(errors, key='status', message='Requests statuses are not able to be updated to waiting.')

        raise_validation_errors(errors)

        return data


class NotExistingRequestSerializer(serializers.ModelSerializer):
    ''' Not existing request serializer '''
    class Meta:
        ''' Meta '''
        model = Request
        fields = '__all__'
        read_only_fields = ('user', 'status', 'updated_by',)

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        request = self.context['request']
        community = data['community']
        user = request.user

        # Case 1: Non-student trying to join the club, or non-student and non-lecturer trying to join the lab
        if has_instance(community, Club):
            if not IsStudent().has_permission(request, None):
                add_error_message(
                    errors, key='community', message='Requests are only able to be made to the club by students.'
                )
        elif has_instance(community, Lab):
            if not IsStudent().has_permission(request, None) and not IsLecturer().has_permission(request, None):
                add_error_message(
                    errors, key='community',
                    message='Requests are only able to be made to the lab by students and lecturers.'
                )

        # Case 2: Community does not accept requests
        if not community.is_accepting_requests:
            add_error_message(
                errors, key='community',
                message='Requests are not able to be made to the community which doesn\'t accept requests.'
            )

        # Case 3: Community is community event and doesn't allow outside participators
        if has_instance(community, CommunityEvent):
            community_event = CommunityEvent.objects.get(pk=community.id)
            if not community_event.allows_outside_participators:
                if not IsMemberOfBaseCommunity().has_object_permission(request, None, community_event):
                    add_error_message(
                        errors, key='community',
                        message='Requests are not able to be made to the community event that does not allow outside ' +
                                'participators.'
                    )

        # Case 4: Already a member
        membership = Membership.objects.filter(community_id=community.id, user_id=user.id, status__in=('A', 'R'))
        if len(membership) >= 1:
            add_error_message(
                errors, key='community',
                message='Requests are not able to be made to the community which the user is already a member.'
            )

        # Case 5: Already has a pending request
        join_request = Request.objects.filter(community_id=community.id, user_id=user.id, status='W')
        if len(join_request) >= 1:
            add_error_message(
                errors, key='community',
                message='Requests are not able to be made to the community if the user already has a pending request.'
            )

        # Case 6: Already has a pending invitation
        invitation = Invitation.objects.filter(community_id=community.id, invitee_id=user.id, status='W')
        if len(invitation) >= 1:
            add_error_message(
                errors, key='community',
                message='Requests are not able to be made if the pending invitation to the community exists.'
            )

        # Case 7: Non-active communities
        if not IsInActiveCommunity().has_object_permission(self.context['request'], None, data['community']):
            add_error_message(
                errors, key='community', message='Requests are not able to be made to non-active communities.'
            )

        raise_validation_errors(errors)

        return data


class ExistingInvitationSerializer(serializers.ModelSerializer):
    ''' Existing invitation serializer '''
    meta = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = Invitation
        fields = '__all__'
        read_only_fields = ('community', 'invitor', 'invitee')

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        if data['status'] == 'W':
            errors['status'] = _('Invitation statuses are not able to be updated to waiting.')

        raise_validation_errors(errors)

        return data

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        return {
            'is_able_to_cancel': self.get_is_able_to_cancel(obj)
        }

    def get_is_able_to_cancel(self, obj):
        ''' Retrieve cancellable status '''
        return IsAbleToDeleteInvitation().has_object_permission(self.context['request'], None, obj)


class NotExistingInvitationSerializer(serializers.ModelSerializer):
    ''' Not existing invitation serializer '''
    class Meta:
        ''' Meta '''
        model = Invitation
        fields = '__all__'
        read_only_fields = ('invitor', 'status')

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        request = self.context['request']
        community = data['community']
        invitor = request.user
        invitee = data['invitee']

        # Case 1: Trying to invite a lecturer or a support staff to join the club, or support staff to join the lab
        if has_instance(community, Club):
            if not IsStudentObject().has_object_permission(request, None, invitee):
                add_error_message(
                    errors, key='invitee',
                    message='Invitation to join the club are only able to be made to students.'
                )
        elif has_instance(community, Lab):
            if not IsStudentObject().has_object_permission(request, None, invitee):
                if not IsLecturerObject().has_object_permission(request, None, invitee):
                    add_error_message(
                        errors, key='invitee',
                        message='Invitation to join the lab are only able to be made to students and lecturers.'
                    )

        # Case 2: Community is community event and doesn't allow outside participators
        if has_instance(community, CommunityEvent):
            community_event = CommunityEvent.objects.get(pk=community.id)
            if not community_event.allows_outside_participators:
                memberships = Membership.objects.filter(
                    user_id=invitee.id, community_id=community_event.created_under.id, status__in=('A', 'R')
                )
                if len(memberships) != 1:
                    add_error_message(
                        errors, key='community',
                        message='Invitation are not able to be made to users who are not a member of base community ' +
                                'due to the community event does not allow outside participators.'
                    )

        # Case 3: Not a staff
        invitor_membership = Membership.objects.filter(
            community_id=community.id, user_id=invitor.id, position__in=[1, 2, 3],status='A'
        )
        if len(invitor_membership) == 0:
            add_error_message(
                errors, message='Invitation are not able to be made from the community if the invitor is not a staff.'
            )

        # Case 4: Already a member
        invitee_membership = Membership.objects.filter(
            community_id=community.id, user_id=invitee.id, status__in=('A', 'R')
        )
        if len(invitee_membership) >= 1:
            add_error_message(
                errors, key='invitee',
                message='Invitation are not able to be made from the community which the invitee is already a member.'
            )

        # Case 5: Already has a pending invitation
        invitation = Invitation.objects.filter(community_id=community.id, invitee_id=invitee.id, status='W')
        if len(invitation) >= 1:
            add_error_message(
                errors, key='invitee',
                message='Invitations are not able to be made from the community if the user already has a pending ' +
                        'invitation.'
            )

        # Case 6: Already has a pending request
        join_request = Request.objects.filter(community_id=community.id, user_id=invitee.id, status='W')
        if len(join_request) >= 1:
            add_error_message(
                errors, key='invitee',
                message='Invitations are not able to be made from the community if the user already has a pending ' +
                        'request.'
            )

        # Case 7: Non-active communities
        if not IsInActiveCommunity().has_object_permission(self.context['request'], None, data['community']):
            add_error_message(
                errors, key='community', message='Invitations are not able to be made from non-active communities.'
            )

        raise_validation_errors(errors)

        return data


class MembershipSerializer(serializers.ModelSerializer):
    ''' Membership serializer '''
    meta = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = Membership
        exclude = ('updated_at', 'created_by', 'updated_by')
        read_only_fields = ('user', 'community')

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        # Loads Original Membership
        original_membership = Membership.objects.get(pk=self.instance.id)

        # Fill Missing Data from Request
        if not field_exists(data, 'status'):
            data['status'] = original_membership.status
        elif not field_exists(data, 'position'):
            data['position'] = original_membership.position

        # Variables for Validation
        user_id = {'new': self.instance.user.id, 'own': self.context['request'].user.id}
        position = {
            'old': original_membership.position,
            'new': data['position'],
            'own': Membership.objects.get(user_id=user_id['own'], community_id=self.instance.community.id).position
        }
        status = {'old': original_membership.status, 'new': data['status']}

        # Update Error
        if (position['old'] != position['new']) and (status['old'] != status['new']):
            add_error_message(
                errors, message='Memberships are not able to be updated both position and status at the same time.'
            )
        elif (position['old'] == position['new']) and (status['old'] == status['new']):
            add_error_message(errors, message='No updates provided for the membership.')

        # Case 1: Leaving and Retiring
        elif user_id['new'] == user_id['own']:
            if position['old'] != position['new']:
                add_error_message(
                    errors, key='position', message='Membership owners are not able to change their own position.'
                )
            elif status['old'] != status['new'] and status['old'] + status['new'] not in ('AR', 'RA', 'AL', 'RL'):
                add_error_message(
                    errors, key='status',
                    message='Membership owners are only able to switch their own membership status from active and ' +
                            'retired to left, or between active and retired.'
                )

        # Case 2: Member Removal
        elif position['old'] == position['new'] and status['old'] != status['new']:
            if not status['old'] in ('A', 'R') or not status['new'] == 'X':
                add_error_message(
                    errors, key='status',
                    message='Membership statuses are only meant to be updated from active or retired to removed if ' +
                            'attempted by other members in the community.'
                )
            elif position['own'] in (0, 1) or position['own'] <= position['new']:
                add_error_message(
                    errors, key='status',
                    message='Membership statuses can only be set to removed on memberships with a lower position by ' +
                            'the leader or the deputy leader of the community.'
                )

        # Case 3: Position Assignation
        elif position['old'] != position['new'] and status['old'] == status['new']:
            if position['own'] in (0, 1):
                add_error_message(
                    errors, key='position',
                    message='Membership positions are not able to be updated by a normal member or a staff.'
                )
            elif position['own'] == 2 and position['new'] in (2, 3):
                add_error_message(
                    errors, key='position',
                    message='Membership positions are not able to be updated to the position equal to or higher than ' +
                            'your own position.'
                )

        raise_validation_errors(errors)

        return data

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        return {
            'is_able_to_assign': self.get_is_able_to_assign(obj),
            'is_able_to_remove': self.get_is_able_to_remove(obj),
            'is_able_to_leave': self.get_is_able_to_leave(obj),
            'is_able_to_vote': self.get_is_able_to_vote(obj),
            'is_able_to_set_custom_label':  self.get_is_able_to_set_custom_label(obj),
            'custom_membership_label': self.get_custom_membership_label(obj)
        }

    def get_is_able_to_assign(self, obj):
        ''' Retrieve assignable positions '''
        # Retrieve own membership
        try:
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.community.id, status='A'
            )
        except Membership.DoesNotExist:
            return list()

        # Own membership, non-active membership, or not having a higher position than the membership
        if membership.id == obj.id or obj.status != 'A' or membership.position <= obj.position:
            return list()

        # Position assignable data - Special case
        if has_instance(obj.community, Lab) and membership.position in (2, 3):
            if not IsLecturerObject().has_object_permission(None, None, obj.user):
                return [
                    {'position': 1, 'is_assignable': (1 != obj.position)},
                    {'position': 0, 'is_assignable': (0 != obj.position)}
                ]

        # Position assignable data - Normal case
        if membership.position == 3:
            return [
                {'position': 3, 'is_assignable': True},
                {'position': 2, 'is_assignable': (2 != obj.position)},
                {'position': 1, 'is_assignable': (1 != obj.position)},
                {'position': 0, 'is_assignable': (0 != obj.position)}
            ]
        elif membership.position == 2:
            return [
                {'position': 1, 'is_assignable': (1 != obj.position)},
                {'position': 0, 'is_assignable': (0 != obj.position)}
            ]
        return list()

    def get_is_able_to_remove(self, obj):
        ''' Retrieve removable status '''
        try:
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.community.id, status='A'
            )

            if membership.id == obj.id:
                return False
            elif membership.position >= 2 and membership.position > obj.position and obj.status in ('A', 'R'):
                return True
            return False
        except Membership.DoesNotExist:
            return False

    def get_is_able_to_leave(self, obj):
        ''' Retrieve leave-able status '''
        return obj.user.id == self.context['request'].user.id and obj.position != 3 and obj.status in ('A', 'R')

    def get_is_able_to_vote(self, obj):
        ''' Retrieve vote-able status '''
        request = self.context['request']

        # Community type must be event
        try:
            event = Event.objects.get(pk=obj.community.id)
        except Event.DoesNotExist:
            return False

        # Event must be approved
        if not event.is_approved:
            return False

        # Must be a member of the event
        if not IsMemberOfCommunity().has_object_permission(request, None, event):
            return False

        # Must already ended
        if not is_ended_event(event):
            return False

        # Must not vote for yourself
        if request.user.id == obj.user.id:
            return False

        # Must not exceed limit after voting
        membership_ids = [i.id for i in Membership.objects.filter(community_id=event.id)]
        user_votes = Vote.objects.filter(voted_for_id__in=membership_ids, voted_by_id=request.user.id)
        if len(user_votes) + 1 > VOTE_LIMIT_PER_EVENT:
            return False

        # Must not be a duplicated vote
        user_votes = user_votes.filter(voted_for_id=obj.id, voted_by_id=request.user.id)
        if len(user_votes) != 0:
            return False

        return True

    def get_is_able_to_set_custom_label(self, obj):
        ''' Retrieve set custom label availability status '''
        try:
            Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.community.id, status='A', position__in=(2, 3)
            )
        except Membership.DoesNotExist:
            return False

        return obj.position in (1, 2)

    def get_custom_membership_label(self, obj):
        ''' Retrieve custom membership label '''
        try:
            if obj.position in (1, 2):
                label = CustomMembershipLabel.objects.get(membership_id=obj.id).label
                if label.strip() != str():
                    return label
                return None
            return None
        except CustomMembershipLabel.DoesNotExist:
            return None


class ExistingCustomMembershipLabelSerializer(serializers.ModelSerializer):
    ''' Existing custom membership label serializer '''
    class Meta:
        ''' Meta '''
        model = CustomMembershipLabel
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('membership',)


class NotExistingCustomMembershipLabelSerializer(serializers.ModelSerializer):
    ''' Not existing custom membership label serializer'''
    class Meta:
        ''' Meta '''
        model = CustomMembershipLabel
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        request = self.context['request']
        community = Community.objects.get(pk=data['membership'].community.id)

        # Case 1: Creator is not a deputy leader
        if not IsDeputyLeaderOfCommunity().has_object_permission(request, None, community):
            add_error_message(
                errors,
                message='Custom membership labels are only able to be created, updated, or deleted by deputy leader ' +
                        'of the community.'
            )

        # Case 2: Labeled member is not staff or deputy leader
        if data['membership'].position not in (1, 2):
            add_error_message(
                errors, key='membership',
                message='Custom membership labels are only applicable on staff and deputy leader.'
            )

        # Case 3: Non-active communities
        if not IsInActiveCommunity().has_object_permission(self.context['request'], None, data['membership']):
            add_error_message(
                errors, key='membership',
                message='Custom membership labels are not able to be created for memberships in non-active communities.'
            )

        validate_profanity_serializer(data, 'label', errors, field_name='Custom membership label')

        raise_validation_errors(errors)

        return data


class MembershipLogSerializer(serializers.ModelSerializer):
    ''' Membership log serializer '''
    meta = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = MembershipLog
        exclude = ('created_by', 'updated_by')
        read_only_fields = ('membership', 'position', 'status', 'start_date', 'end_date')

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        return {
            'user': self.get_user(obj),
            'community': self.get_community(obj),
            'log_text': self.get_log_text(obj),
            'log_text_th': self.get_log_text_th(obj)
        }

    def get_user(self, obj):
        ''' Retrieve user ID '''
        return obj.membership.user.id

    def get_community(self, obj):
        ''' Retrieve community id '''
        return obj.membership.community.id

    def get_log_text(self, obj, use_community_name=False):
        ''' Retrieve log text '''
        previous = get_previous_membership_log(obj)

        # Retrieve the community type
        community_type = 'the community'

        if use_community_name:
            community_type = obj.membership.community.name_en
        elif has_instance(obj.membership.community, Club):
            community_type = 'the club'
        elif has_instance(obj.membership.community, CommunityEvent):
            community_type = 'the community event'
        elif has_instance(obj.membership.community, Event):
            community_type = 'the event'
        elif has_instance(obj.membership.community, Lab):
            community_type = 'the lab'

        # If the first log
        if previous is None:
            return _('{} has joined {}.'.format(obj.membership.user.name, community_type))

        # If not the first log, the difference is the status
        if previous.status != obj.status:
            if (previous.status, obj.status) == ('R', 'A'):
                return _('{} is back in duty.'.format(obj.membership.user.name))
            elif obj.status == 'A':
                return _('{} has joined {}.'.format(obj.membership.user.name, community_type))
            elif obj.status == 'R':
                return _('{} has retired from {}.'.format(obj.membership.user.name, community_type))
            elif obj.status == 'L':
                return _('{} has left {}.'.format(obj.membership.user.name, community_type))
            elif obj.status == 'X':
                return _('{} is removed from {} by {}.'.format(
                    obj.membership.user.name, community_type, obj.created_by.name
                ))

        # If not the first log, the difference is the position
        elif previous.position != obj.position:
            if obj.position == 0:
                return _('{} is demoted to member by {}.'.format(obj.membership.user.name, obj.updated_by.name))
            elif previous.position > obj.position and obj.position == 1:
                return _('{} is demoted to staff by {}.'.format(obj.membership.user.name, obj.updated_by.name))
            elif previous.position < obj.position and obj.position == 1:
                return _('{} is promoted to staff by {}.'.format(obj.membership.user.name, obj.updated_by.name))
            elif previous.position > obj.position and obj.position == 2:
                return _('{} is demoted to deputy leader.'.format(obj.membership.user.name))
            elif previous.position < obj.position and obj.position == 2:
                return _('{} is promoted to deputy leader by {}.'.format(obj.membership.user.name, obj.updated_by.name))
            elif obj.position == 3:
                return _('{} is promoted to leader by {}.'.format(obj.membership.user.name, obj.updated_by.name))

        return None

    def get_log_text_th(self, obj, use_community_name=False):
        ''' Retrieve log text in the Thai language '''
        previous = get_previous_membership_log(obj)

        # Retrieve the community type
        community_type = 'สังคม'

        if use_community_name:
            community_type = ' ' + obj.membership.community.name_th + ' '
        elif has_instance(obj.membership.community, Club):
            community_type = 'ชุมนุม'
        elif has_instance(obj.membership.community, CommunityEvent):
            if has_instance(CommunityEvent.objects.get(pk=obj.membership.community.id).created_under, Club):
                community_type = 'กิจกรรมชุมนุม'
            elif has_instance(CommunityEvent.objects.get(pk=obj.membership.community.id).created_under, Lab):
                community_type = 'กิจกรรมห้องปฏิบัติการ'
        elif has_instance(obj.membership.community, Event):
            community_type = 'กิจกรรม'
        elif has_instance(obj.membership.community, Lab):
            community_type = 'ห้องปฏิบัติการ'

        # If the first log
        if previous is None:
            return _('{} ได้เข้าร่วม{}'.format(obj.membership.user.name, community_type))

        # If not the first log, the difference is the status
        if previous.status != obj.status:
            if (previous.status, obj.status) == ('R', 'A'):
                return _('{} ได้กลับมาเป็นสมาชิก'.format(obj.membership.user.name))
            elif obj.status == 'A':
                return _('{} ได้เข้าร่วม{}'.format(obj.membership.user.name, community_type))
            elif obj.status == 'R':
                return _('{} ได้ถอนตัวจาก{}'.format(obj.membership.user.name, community_type))
            elif obj.status == 'L':
                return _('{} ได้ออกจาก{}'.format(obj.membership.user.name, community_type))
            elif obj.status == 'X':
                return _('{} ถูกนำออกจาก{}โดย {}'.format(obj.membership.user.name, community_type, obj.created_by.name))

        # If not the first log, the difference is the position
        elif previous.position != obj.position:
            if obj.position == 0:
                return _('{} ถูกลดระดับเป็นสมาชิกโดย {}'.format(obj.membership.user.name, obj.updated_by.name))
            elif previous.position > obj.position and obj.position == 1:
                return _('{} ถูกลดระดับเป็นทีมงานโดย {}'.format(obj.membership.user.name, obj.updated_by.name))
            elif previous.position < obj.position and obj.position == 1:
                return _('{} ถูกยกระดับเป็นทีมงานโดย {}'.format(obj.membership.user.name, obj.updated_by.name))
            elif previous.position > obj.position and obj.position == 2:
                return _('{} ถูกลดระดับเป็นรองประธาน'.format(obj.membership.user.name))
            elif previous.position < obj.position and obj.position == 2:
                return _('{} ถูกเพิ่มระดับเป็นรองประธานโดย {}'.format(obj.membership.user.name, obj.updated_by.name))
            elif obj.position == 3:
                return _('{} ถูกแต่งตั้งเป็นประธานโดย {}'.format(obj.membership.user.name, obj.updated_by.name))

        return None


class AdvisorySerializer(serializers.ModelSerializer):
    ''' Advisory serializer '''
    meta = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = Advisory
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        # Advisor validation
        if not IsLecturerObject().has_object_permission(self.context['request'], None, data['advisor']):
            add_error_message(errors, key='advisor', message='Advisor must be a lecturer.')

        # Community type validation
        if has_instance(data['community'], Lab) or has_instance(data['community'], CommunityEvent):
            add_error_message(errors, key='community', message='Community must be a club or an event.')

        # Dates validation
        if data['start_date'] > data['end_date']:
            add_error_message(errors, key='start_date', message='Start date must come before end date.')
            add_error_message(errors, key='end_date', message='End date must come after start date.')

        # Overlapping validation
        advisories = Advisory.objects.filter(community_id=data['community'].id)
        for i in advisories:
            if data['start_date'] <= i.end_date and i.start_date <= data['end_date']:
                add_error_message(
                    errors, message='Advisory time overlapped. A community can only have one advisor at a time.'
                )

        # Non-active communities
        if not IsInActiveCommunity().has_object_permission(self.context['request'], None, data['community']):
            add_error_message(
                errors, key='community', message='Advisories are not able to be created for non-active communities.'
            )

        raise_validation_errors(errors)

        return data

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        return {
            'advisor_name': self.get_advisor_name(obj),
            'community_name': self.get_community_name(obj),
            'is_active': self.get_is_active(obj)
        }

    def get_advisor_name(self, obj):
        ''' Retrieve name of the advisor '''
        return obj.advisor.name

    def get_community_name(self, obj):
        ''' Retrieve name of the community '''
        return obj.community.name_en

    def get_is_active(self, obj):
        ''' Retrieve active status '''
        return obj.start_date <= datetime.now().date() <= obj.end_date


class ExistingApprovalRequestSerializer(serializers.ModelSerializer):
    ''' Existing approval request serializer '''
    class Meta:
        ''' Meta '''
        model = ApprovalRequest
        fields = '__all__'
        read_only_fields = ('community', 'message', 'attached_file', 'created_by', 'updated_by')

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        if data['status'] == 'W':
            errors['status'] = _('Approval request statuses are not able to be updated to waiting.')

        raise_validation_errors(errors)

        return data


class NotExistingApprovalRequestSerializer(serializers.ModelSerializer):
    ''' Not existing approval request serializer '''
    class Meta:
        ''' Meta '''
        model = ApprovalRequest
        fields = '__all__'
        read_only_fields = ('status', 'created_by', 'updated_by')

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        request = self.context['request']
        community = data['community']

        # Case 1: Must be not be a community event or a lab
        if has_instance(community, CommunityEvent):
            add_error_message(
                errors, key='community', message='Approval requests are not able to be made from community events.'
            )
        elif has_instance(community, Lab):
            add_error_message(errors, key='community', message='Approval requests are not able to be made from labs.')

        # Case 2: Must be an unofficial or renewable club, or an unapproved event
        if has_instance(community, Club):
            if not IsRenewableClub().has_object_permission(request, None, Club.objects.get(pk=community.id)):
                add_error_message(
                    errors, key='community', message='The club is still valid and not ready for renewal yet.'
                )
        elif has_instance(community, Event):
            if Event.objects.get(pk=community.id).is_approved:
                add_error_message(errors, key='community', message='The event is already approved.')

        # Case 3: Approval request sender must be the president of the club or event
        if not IsLeaderOfCommunity().has_object_permission(request, None, community):
            add_error_message(
                errors, key='community', message='Approval requests can only be made by the leader of the community.'
            )

        # Case 4: Already has pending approval request
        approval_request = ApprovalRequest.objects.filter(community_id=community.id, status='W')
        if len(approval_request) >= 1:
            add_error_message(
                errors, key='community',
                message='Approval requests are not able to be made if the community already has a pending approval ' +
                        'request.'
            )

        # Case 5: Non-active communities
        if not IsInActiveCommunity().has_object_permission(self.context['request'], None, data['community']):
            add_error_message(
                errors, key='community',
                message='Approval requests are not able to be made from non-active communities.'
            )

        validate_profanity_serializer(data, 'message', errors, field_name='Approval request message')

        raise_validation_errors(errors)

        return data
