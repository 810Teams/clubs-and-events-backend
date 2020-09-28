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
