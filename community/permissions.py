from rest_framework import permissions

from community.models import Community
from membership.models import Membership


class IsPubliclyVisibleCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Community
        if not request.user.is_authenticated and not obj.is_publicly_visible:
            return False
        return True


class IsLeaderOfBaseCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: CommunityEvent
        base_community = Community.objects.get(pk=obj.created_under.id)
        base_membership = Membership.objects.filter(
            user_id=request.user.id, position__in=[3], community_id=base_community.id, status='A'
        )

        return len(base_membership) == 1


class IsDeputyLeaderOfBaseCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: CommunityEvent
        base_community = Community.objects.get(pk=obj.created_under.id)
        base_membership = Membership.objects.filter(
            user_id=request.user.id, position__in=[2, 3], community_id=base_community.id, status='A'
        )

        return len(base_membership) == 1


class IsStaffOfBaseCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: CommunityEvent
        base_community = Community.objects.get(pk=obj.created_under.id)
        base_membership = Membership.objects.filter(
            user_id=request.user.id, position__in=[1, 2, 3], community_id=base_community.id, status='A'
        )

        return len(base_membership) == 1


class IsMemberOfBaseCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: CommunityEvent
        base_community = Community.objects.get(pk=obj.created_under.id)
        base_membership = Membership.objects.filter(
            user_id=request.user.id, community_id=base_community.id, status='A'
        )

        return len(base_membership) == 1


# TODO: Implements a better deletable condition
class IsDeletableClub(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Club
        return not obj.is_official


# TODO: Implements a better deletable condition
class IsDeletableEvent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Event
        return not obj.is_approved


# TODO: Implements a better deletable condition
class IsDeletableCommunityEvent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Community Event
        return True


# TODO: Implements a better deletable condition
class IsDeletableLab(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Lab
        return True
