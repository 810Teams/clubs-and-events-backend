from rest_framework import permissions

from membership.models import Membership


class IsRequestOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Request
        return request.user.id == obj.user.id


class IsWaitingRequest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Request
        return obj.status == 'W'


class IsAbleToViewRequestList(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Request
        # Condition: If is membership of the community or is the sender of the request
        membership = Membership.objects.filter(
            user_id=request.user.id, community_id=obj.community.id, status__in=('A', 'R')
        )
        return len(membership) == 1 or request.user.id == obj.user.id


class IsAbleToCancelInvitation(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Invitation
        if obj.status != 'W':
            return False
        if request.user.id == obj.invitor:
            return True

        try:
            Membership.objects.get(
                user=request.user.id, community_id=obj.community.id, status='A', position__in=(2, 3)
            )
            return True
        except Membership.DoesNotExist:
            return False


class IsInvitationInvitee(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Invitation
        return request.user.id == obj.invitee.id


class IsWaitingInvitation(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Invitation
        return obj.status == 'W'


class IsAbleToViewInvitationList(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Invitation
        # Condition: If is membership of the community or is the invitee of the invitation
        membership = Membership.objects.filter(
            user_id=request.user.id, community_id=obj.community.id, status__in=('A', 'R')
        )
        return len(membership) == 1 or request.user.id == obj.invitee.id


class IsAbleToUpdateMembership(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Membership
        # Prerequisite 1: Memberships with a status of 'L' or 'R' are not able to be updated
        if obj.status in ('L', 'R'):
            return False

        # Prerequisite 2: Memberships with a position of 3 are not able to be updated
        if obj.position == 3:
            return False

        # Case 1: Leaving and retiring, must be the membership owner.
        is_membership_owner = request.user.id == obj.user.id and obj.position not in ('L', 'X')

        # Case 2: Member removal and position assignation, must be done by an active deputy leader of the community,
        #         and not be done on memberships with position equal to yourself.
        own_membership = Membership.objects.filter(
            user_id=request.user.id, community_id=obj.community.id, position__in=(2, 3), status='A'
        )
        is_deputy_leader_of_that_community = len(own_membership) == 1 and own_membership[0].position > obj.position

        return is_membership_owner or is_deputy_leader_of_that_community


class IsApplicableForCustomMembershipLabel(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: CustomMembershipLabel
        return obj.membership.position in (1, 2)
