from rest_framework import permissions

from community.models import Club, Lab, Community
from membership.models import Membership


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='student').exists()


class IsLecturer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='lecturer').exists()


class IsPubliclyVisible(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Community
        if not request.user.is_authenticated and not obj.is_publicly_visible:
            return False
        return True


class IsLeaderOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Community
        membership = Membership.objects.filter(
            user_id=request.user.id, position__in=[3], community_id=obj.id, end_date=None
        )
        return len(membership) == 1


class IsDeputyLeaderOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Community
        membership = Membership.objects.filter(
            user_id=request.user.id, position__in=[2, 3], community_id=obj.id, end_date=None
        )
        return len(membership) == 1


class IsStaffOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Community
        membership = Membership.objects.filter(
            user_id=request.user.id, position__in=[1, 2, 3], community_id=obj.id, end_date=None
        )
        return len(membership) == 1


class IsMemberOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Community
        membership = Membership.objects.filter(
            user_id=request.user.id, community_id=obj.id, end_date=None
        )
        return len(membership) == 1


class IsLeaderOfBaseCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        base_community = Community.objects.get(pk=obj.created_under.id)
        base_membership = Membership.objects.filter(
            user_id=request.user.id, position__in=[3], community_id=base_community.id, end_date=None
        )

        return len(base_membership) == 1


class IsDeputyLeaderOfBaseCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        base_community = Community.objects.get(pk=obj.created_under.id)
        base_membership = Membership.objects.filter(
            user_id=request.user.id, position__in=[2, 3], community_id=base_community.id, end_date=None
        )

        return len(base_membership) == 1


class IsStaffOfBaseCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        base_community = Community.objects.get(pk=obj.created_under.id)
        base_membership = Membership.objects.filter(
            user_id=request.user.id, position__in=[1, 2, 3], community_id=base_community.id, end_date=None
        )

        return len(base_membership) == 1


class IsMemberOfBaseCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        base_community = Community.objects.get(pk=obj.created_under.id)
        base_membership = Membership.objects.filter(
            user_id=request.user.id, community_id=base_community.id, end_date=None
        )

        return len(base_membership) == 1


class IsDeletableClub(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.is_official


class IsDeletableEvent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.is_approved or obj.is_cancelled


class IsDeletableCommunityEvent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.is_cancelled


# TODO: Implements lab deletable condition
class IsDeletableLab(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Community
        return True
