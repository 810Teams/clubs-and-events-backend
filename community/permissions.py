from rest_framework import permissions

from membership.models import Membership


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='student').exists()


class IsLecturer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='lecturer').exists()


class IsPubliclyVisible(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated and not obj.is_publicly_visible:
            return False
        return True


class IsPresidentOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        membership = Membership.objects.filter(
            user_id=request.user.id, position=3, community_id=obj.id, end_date=None
        )
        return len(membership) == 1


class IsVicePresidentOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        membership = Membership.objects.filter(
            user_id=request.user.id, position__in=[2, 3], community_id=obj.id, end_date=None
        )
        return len(membership) == 1


class IsDeletableClub(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.is_official
