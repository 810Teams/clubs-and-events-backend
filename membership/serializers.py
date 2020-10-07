from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import serializers

from community.models import Community, CommunityEvent, Club
from membership.models import Request, Invitation, Membership, CustomMembershipLabel, Advisory, MembershipLog


class ExistingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'
        read_only_fields = ('user', 'community', 'updated_by')

    def validate(self, data):
        if data['status'] == 'W':
            raise serializers.ValidationError(
                _('Requests statuses are not able to be updated to waiting.'),
                code='request_status_error'
            )
        return data


class NotExistingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'
        read_only_fields = ('user', 'status', 'updated_by',)

    def validate(self, data):
        community_id = data['community'].id
        user_id = self.context['request'].user.id

        # Case 1: Lecturer trying to request to join the club
        try:
            Club.objects.get(pk=community_id)
            if self.context['request'].user.is_lecturer:
                raise serializers.ValidationError(
                    _('Requests are not able to be made to the club by a lecturer.'),
                    code='lecturer_limits'
                )
        except Club.DoesNotExist:
            pass

        # Case 2: Community does not accept requests
        community = Community.objects.get(pk=community_id)
        if not community.is_accepting_requests:
            raise serializers.ValidationError(
                _('Requests are not able to be made to the community which doesn\'t accept requests.'),
                code='community_not_accepting_requests'
            )

        # Case 3: Community is community event and doesn't allow outside participators
        try:
            community_event = CommunityEvent.objects.get(pk=community_id)
            base_community = Community.objects.get(pk=community_event.created_under.id)
            base_membership = Membership.objects.filter(
                user_id=self.context['request'].user.id, position__in=[1, 2, 3], community_id=base_community.id,
                status='A'
            )
            if not community_event.allows_outside_participators and len(base_membership) != 1:
                raise serializers.ValidationError(
                    _('Requests are not able to be made to the community event that does not allow outside ' +
                      'participators.'),
                    code='outside_participator_disallowed'
                )
        except CommunityEvent.DoesNotExist:
            pass

        # Case 4: Already a member
        membership = Membership.objects.filter(community_id=community_id, user_id=user_id, status__in=('A', 'R'))
        if len(membership) == 1:
            raise serializers.ValidationError(
                _('Requests are not able to be made to the community which the user is already a member.'),
                code='member_already_exists'
            )

        # Case 5: Already has a pending request
        request = Request.objects.filter(community_id=community_id, user_id=user_id, status='W')
        if len(request) == 1:
            raise serializers.ValidationError(
                _('Requests are not able to be made to the community if the user already has a pending request.'),
                code='request_already_exists'
            )

        # Case 6: Already has a pending invitation
        invitation = Invitation.objects.filter(community_id=community_id, invitee_id=user_id, status='W')
        if len(invitation) == 1:
            raise serializers.ValidationError(
                _('Requests are not able to be made if the pending invitation to the community exists.'),
                code='invitation_already_exists'
            )

        return data


class ExistingInvitationSerializer(serializers.ModelSerializer):
    is_able_to_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = '__all__'
        read_only_fields = ('community', 'invitor', 'invitee')

    def validate(self, data):
        if data['status'] == 'W':
            raise serializers.ValidationError(
                _('Invitation statuses are not able to be updated to waiting.'),
                code='invitation_status_error'
            )
        return data

    def get_is_able_to_cancel(self, obj):
        if obj.status != 'W':
            return False
        if self.context['request'].user.id == obj.invitor:
            return True

        try:
            Membership.objects.get(
                user=self.context['request'].user.id, community_id=obj.community.id, status='A', position__in=(2, 3)
            )
            return True
        except Membership.DoesNotExist:
            return False


class NotExistingInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'
        read_only_fields = ('invitor', 'status')

    def validate(self, data):
        community_id = data['community'].id
        invitor_id = self.context['request'].user.id
        invitee_id = data['invitee'].id

        # Case 1: Trying to invite a lecturer to join the club
        try:
            Club.objects.get(pk=community_id)
            if get_user_model().objects.get(pk=invitee_id).is_lecturer:
                raise serializers.ValidationError(
                    _('Invitation to join the club are not able to be made to lecturers.'),
                    code='lecturer_limits'
                )
        except Club.DoesNotExist:
            pass

        # Case 2: Community is community event and doesn't allow outside participators
        try:
            community_event = CommunityEvent.objects.get(pk=community_id)
            base_community = Community.objects.get(pk=community_event.created_under.id)
            base_membership = Membership.objects.filter(
                user_id=data['invitee'].id, community_id=base_community.id, status__in=('A', 'R')
            )
            if not community_event.allows_outside_participators and len(base_membership) != 1:
                raise serializers.ValidationError(
                    _('Invitation are not able to be made from the community event that does not allow outside ' +
                      'participators.'),
                    code='outside_participator_disallowed'
                )
        except CommunityEvent.DoesNotExist:
            pass

        # Case 3: Not a staff
        invitor_membership = Membership.objects.filter(
            community_id=community_id, user_id=invitor_id, position__in=[1, 2, 3],status='A'
        )
        if len(invitor_membership) != 1:
            raise serializers.ValidationError(
                _('Invitation are not able to be made from the community if the invitor is not a staff.'),
                code='permission_denied'
            )

        # Case 4: Already a member
        invitee_membership = Membership.objects.filter(
            community_id=community_id, user_id=invitee_id, status__in=('A', 'R')
        )
        if len(invitee_membership) == 1:
            raise serializers.ValidationError(
                _('Invitation are not able to be made from the community which the invitee is already a member.'),
                code='member_already_exists'
            )

        # Case 5: Already has a pending request
        invitation = Invitation.objects.filter(community_id=community_id, invitee_id=invitee_id, status='W')
        if len(invitation) == 1:
            raise serializers.ValidationError(
                _('Invitations are not able to be made from the community if the invitee already has a pending ' +
                  'request.'),
                code='invitation_already_exists'
            )

        # Case 6: Already has a pending invitation
        request = Request.objects.filter(community_id=community_id, user_id=invitee_id, status='W')
        if len(request) == 1:
            raise serializers.ValidationError(
                _('Invitations are not able to be made from the community if the user already has a pending request.'),
                code='request_already_exists'
            )

        return data


class MembershipSerializer(serializers.ModelSerializer):
    is_able_to_assign = serializers.SerializerMethodField()
    is_able_to_remove = serializers.SerializerMethodField()
    is_able_to_leave = serializers.SerializerMethodField()
    custom_membership_label = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = '__all__'
        read_only_fields = ('user', 'community', 'created_by', 'updated_by')

    def validate(self, data):
        original_membership = Membership.objects.get(pk=self.instance.id)

        user_id = {'new': self.instance.user.id, 'own': self.context['request'].user.id}
        position = {
            'old': original_membership.position,
            'new': data['position'],
            'own': Membership.objects.get(user_id=user_id['own'], community_id=self.instance.community.id).position
        }
        status = {'old': original_membership.status, 'new': data['status']}

        # Validation
        if position['new'] not in (0, 1, 2, 3):
            raise serializers.ValidationError(
                _('Membership position must be a number from 0 to 3.'),
                code='membership_error'
            )

        # Case 1: Leaving and Retiring
        if user_id['new'] == user_id['own']:
            if position['old'] != position['new']:
                raise serializers.ValidationError(
                    _('Membership owners are not able to change their own position.'),
                    code='membership_error'
                )
            elif status['old'] != status['new'] and status['old'] + status['new'] not in ('AR', 'RA', 'AL', 'RL'):
                raise serializers.ValidationError(
                    _('Membership owners are only able to switch their own membership status from active and ' +
                    'retired to left, or between active and retired.'),
                    code='membership_error'
                )

        # Case 2: Member Removal
        elif position['old'] == position['new'] and status['old'] != status['new']:
            if not status['old'] in ('A', 'R') or not status['new'] == 'X':
                raise serializers.ValidationError(
                    _('Membership statuses are only meant to be updated from active or retired to removed if ' +
                      'attempted by other members in the community.'),
                    code='membership_error'
                )
            elif position['own'] in (0, 1) or position['own'] <= position['new']:
                raise serializers.ValidationError(
                    _('Membership statuses can only be set to removed on memberships with a lower position by the ' +
                    'leader or the deputy leader of the community.'),
                    code='membership_error'
                )

        # Case 3: Position Assignation
        elif position['old'] != position['new'] and status['old'] == status['new']:
            if position['own'] in (0, 1):
                raise serializers.ValidationError(
                    _('Membership positions are not able to be updated by a normal member or a staff.'),
                    code='membership_error'
                )
            elif position['own'] == 2 and position['new'] in (2, 3):
                raise serializers.ValidationError(
                    _('Membership positions are not able to be updated to the position equal to or higher than your ' +
                      'own position.'),
                    code='membership_error'
                )

        # Case 4: Error
        elif position['old'] != position['new'] and status['old'] != status['new']:
            raise serializers.ValidationError(
                _('Memberships are not able to be updated both position and status at the same time.'),
                code='membership_error'
            )

        return data

    def get_is_able_to_assign(self, obj):
        try:
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.community.id, status='A'
            )

            if membership.id == obj.id or obj.status not in ('A', 'R') or membership.position <= obj.position:
                return list()

            return [i for i in range(0, membership.position + (membership.position == 3)) if i != obj.position]
        except Membership.DoesNotExist:
            return list()

    def get_is_able_to_remove(self, obj):
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
        return obj.user.id == self.context['request'].user.id and obj.position != 3 and obj.status in ('A', 'R')

    def get_custom_membership_label(self, obj):
        try:
            return CustomMembershipLabel.objects.get(membership_id=obj.id).label
        except CustomMembershipLabel.DoesNotExist:
            return None


class ExistingCustomMembershipLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomMembershipLabel
        fields = '__all__'
        read_only_fields = ('membership', 'created_by', 'updated_by')


class NotExistingCustomMembershipLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomMembershipLabel
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

    def validate(self, data):
        membership = Membership.objects.filter(
            user_id=self.context['request'].user.id,
            position__in=(2, 3),
            community_id=Community.objects.get(
                pk=data['membership'].community.id
            ),
            status='A'
        )

        # Case 1: Creator is not a deputy leader
        if len(membership) == 0:
            raise serializers.ValidationError(
                _('Custom membership labels are only able to be created, updated, or deleted by deputy leader of ' +
                  'the community.'),
                code='permission_denied'
            )

        # Case 2: Labeled member is not staff or deputy leader
        if data['membership'].position not in (1, 2):
            raise serializers.ValidationError(
                _('Custom membership labels are only applicable on staff and deputy leader.'),
                code='custom_membership_label_limitations'
            )

        return data


class AdvisorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Advisory
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

    def validate(self, data):
        if not data['advisor'].is_lecturer:
            raise serializers.ValidationError(
                _('Advisor must be a lecturer.'),
                code='invalid_advisor'
            )

        advisors = Advisory.objects.filter(advisor_id=data['advisor'].id)
        for i in advisors:
            if data['start_date'] <= i.end_date or i.start_date <= data['end_date']:
                raise serializers.ValidationError(
                    _('Advisory time overlapped.'),
                    code='advisory_overlap'
                )

        return data


class MembershipLogSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    community = serializers.SerializerMethodField()
    community_name_th = serializers.SerializerMethodField()
    community_name_en = serializers.SerializerMethodField()

    class Meta:
        model = MembershipLog
        fields = '__all__'
        read_only_fields = ('membership', 'position', 'status', 'start_date', 'end_date')

    def get_user(self, obj):
        return obj.membership.user.id

    def get_community(self, obj):
        return obj.membership.community.id

    def get_community_name_th(self, obj):
        return obj.membership.community.name_th

    def get_community_name_en(self, obj):
        return obj.membership.community.name_en
