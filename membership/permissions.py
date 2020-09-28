from rest_framework import permissions

from membership.models import Membership


class IsRequestOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Request
        return request.user.id == obj.user.id


class IsEditableRequest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Request
        return obj.status == 'W'


class IsCancellableRequest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Request
        return obj.status == 'W'


class IsAbleToViewRequestList(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Request
        # Condition: If is membership of the community or is the sender of the request
        membership = Membership.objects.filter(user_id=request.user.id, community_id=obj.community.id, status='A')

        return len(membership) == 1 or request.user.id == obj.user.id


class IsInvitationInvitor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Invitation
        return request.user.id == obj.invitor.id


class IsInvitationInvitee(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Invitation
        return request.user.id == obj.invitor.id


class IsEditableInvitation(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Invitation
        return obj.status == 'W'


class IsCancellableInvitation(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Invitation
        return obj.status == 'W'


class IsAbleToViewInvitationList(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Invitation
        # Condition: If is membership of the community or is the invitor or the invitee of the invitation
        membership = Membership.objects.filter(user_id=request.user.id, community_id=obj.community.id, status='A')

        return len(membership) == 1 or request.user.id == obj.invitor.id or request.user.id == obj.invitee.id


class IsAbleToUpdateMembership(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Membership
        # Case 1: Leaving and Retiring, must be the membership owner.
        is_membership_owner = request.user.id == obj.user.id and obj.position not in ('L', 'X')

        # Case 2: Member Removal and Position Assignation, must be an active deputy leader of the community.
        membership = Membership.objects.filter(
            user_id=request.user.id, community_id=obj.community.id, position__in=(2, 3), status='A'
        )
        is_deputy_leader_of_that_community = len(membership) == 1

        # Both Cases: Leader memberships are not able to be updated by anyone.
        object_is_not_leader = obj.position != 3

        return (is_membership_owner or is_deputy_leader_of_that_community) and object_is_not_leader
