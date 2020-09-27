from django.utils.translation import gettext as _
from rest_framework import serializers

from community.models import Community
from membership.models import Request, Invitation, Membership


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
        errors = list()

        community_id = data['community'].id
        user_id = self.context['request'].user.id

        membership = Membership.objects.filter(community_id=community_id, user_id=user_id, status__in=('A', 'R'))
        if len(membership) == 1:
            errors.append(serializers.ValidationError(
                _('Requests are not able to be made to the community which the user is already a member.'),
                code='member_already_exists'
            ))

        request = Request.objects.filter(community_id=community_id, user_id=user_id, status='W')
        if len(request) == 1:
            errors.append(serializers.ValidationError(
                _('Requests are not able to be made to the community if the user already has a pending request.'),
                code='request_already_exists'
            ))

        community = Community.objects.get(pk=community_id)
        if not community.is_accepting_requests:
            errors.append(serializers.ValidationError(
                _('Requests are not able to be made to the community which doesn\'t accept requests.'),
                code='community_not_accepting_requests'
            ))

        if len(errors) > 0:
            raise serializers.ValidationError(errors)

        return data


class ExistingInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'
        read_only_fields = ('community', 'invitor', 'invitee')

    # TODO: Implements validate invitation status


class NotExistingInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'
        read_only_fields = ('invitor', 'status')


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = '__all__'
        read_only_fields = ('user', 'community', 'created_by', 'updated_by')
