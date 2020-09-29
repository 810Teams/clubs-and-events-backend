from django.utils.translation import gettext as _
from rest_framework import serializers

from community.models import Community, CommunityEvent
from membership.models import Request, Invitation, Membership, CustomMembershipLabel


class ExistingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'
        read_only_fields = ('user', 'community', 'updated_by')


class NotExistingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'
        read_only_fields = ('user', 'status', 'updated_by',)

    def validate(self, data):
        community_id = data['community'].id
        user_id = self.context['request'].user.id

        # Case 1: Community does not accept requests
        community = Community.objects.get(pk=community_id)
        if not community.is_accepting_requests:
            raise serializers.ValidationError(
                _('Requests are not able to be made to the community which doesn\'t accept requests.'),
                code='community_not_accepting_requests'
            )

        # Case 2: Community is community event and doesn't allow outside participators
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

        # Case 3: Already a member
        membership = Membership.objects.filter(community_id=community_id, user_id=user_id, status__in=('A', 'R'))
        if len(membership) == 1:
            raise serializers.ValidationError(
                _('Requests are not able to be made to the community which the user is already a member.'),
                code='member_already_exists'
            )

        # Case 4: Already has a pending request
        request = Request.objects.filter(community_id=community_id, user_id=user_id, status='W')
        if len(request) == 1:
            raise serializers.ValidationError(
                _('Requests are not able to be made to the community if the user already has a pending request.'),
                code='request_already_exists'
            )

        # Case 5: Already has a pending invitation
        invitation = Invitation.objects.filter(community_id=community_id, invitee_id=user_id, status='W')
        if len(invitation) == 1:
            raise serializers.ValidationError(
                _('Requests are not able to be made if the pending invitation to the community exists.'),
                code='invitation_already_exists'
            )

        return data


class ExistingInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'
        read_only_fields = ('community', 'invitor', 'invitee')


class NotExistingInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'
        read_only_fields = ('invitor', 'status')

    def validate(self, data):
        community_id = data['community'].id
        invitor_id = self.context['request'].user.id
        invitee_id = data['invitee'].id

        # Case 1: Community is community event and doesn't allow outside participators
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

        # Case 2: Not a staff
        invitor_membership = Membership.objects.filter(
            community_id=community_id, user_id=invitor_id, position__in=[1, 2, 3],status='A'
        )
        if len(invitor_membership) != 1:
            raise serializers.ValidationError(
                _('Invitation are not able to be made from the community if the invitor is not a staff.'),
                code='permission_denied'
            )

        # Case 3: Already a member
        invitee_membership = Membership.objects.filter(
            community_id=community_id, user_id=invitee_id, status__in=('A', 'R')
        )
        if len(invitee_membership) == 1:
            raise serializers.ValidationError(
                _('Invitation are not able to be made from the community which the invitee is already a member.'),
                code='member_already_exists'
            )

        # Case 4: Already has a pending request
        invitation = Invitation.objects.filter(community_id=community_id, invitee_id=invitee_id, status='W')
        if len(invitation) == 1:
            raise serializers.ValidationError(
                _('Invitations are not able to be made from the community if the invitee already has a pending ' +
                  'request.'),
                code='invitation_already_exists'
            )

        # Case 5: Already has a pending invitation
        request = Request.objects.filter(community_id=community_id, user_id=invitee_id, status='W')
        if len(request) == 1:
            raise serializers.ValidationError(
                _('Invitations are not able to be made from the community if the user already has a pending request.'),
                code='request_already_exists'
            )

        return data


class MembershipSerializer(serializers.ModelSerializer):
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
            elif position['own'] == 2 and position['old'] in (2, 3):
                raise serializers.ValidationError(
                    _('Membership positions are not able to be updated if the position is already equal to or higher ' +
                    'than your position.'),
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
