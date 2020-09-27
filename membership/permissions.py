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


class IsMemberOfCommunityOrRequestOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Request
        membership = Membership.objects.filter(user_id=request.user.id, community_id=obj.community.id, status='A')

        return len(membership) == 1 or request.user.id == obj.user.id
