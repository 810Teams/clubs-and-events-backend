'''
    Community Application Permissions
    community/permissions.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from datetime import datetime

from rest_framework import permissions

from clubs_and_events.settings import CLUB_ADVANCED_RENEWAL
from community.models import Community, Club, Event, CommunityEvent, Lab
from core.permissions import IsDeputyLeaderOfCommunity, IsLeaderOfCommunity
from membership.models import Membership
from user.permissions import IsStudent, IsLecturer


class IsAbleToUpdateClub(permissions.BasePermission):
    ''' Main permission of PUT, PATCH request of Club '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Club):
            return IsStudent().has_permission(request, view) \
                   and IsDeputyLeaderOfCommunity().has_object_permission(request, view, obj)
        return False


class IsAbleToDeleteClub(permissions.BasePermission):
    ''' Main permission of DELETE request of Club '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Club):
            return IsStudent().has_permission(request, view) \
                   and IsLeaderOfCommunity().has_object_permission(request, view, obj) \
                   and IsDeletableClub().has_object_permission(request, view, obj)
        return False


class IsAbleToDeleteEvent(permissions.BasePermission):
    ''' Main permission of DELETE request of Event '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Event):
            return IsLeaderOfCommunity().has_object_permission(request, view, obj) \
                   and IsDeletableEvent().has_object_permission(request, view, obj)
        return False


class IsAbleToUpdateCommunityEvent(permissions.BasePermission):
    ''' Main permission of PUT, PATCH request of CommunityEvent '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, CommunityEvent):
            return IsDeputyLeaderOfCommunity().has_object_permission(request, view, obj) \
                   or IsDeputyLeaderOfBaseCommunity().has_object_permission(request, view, obj)
        return False


class IsAbleToDeleteCommunityEvent(permissions.BasePermission):
    ''' Main permission of DELETE request of CommunityEvent '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, CommunityEvent):
            return (IsLeaderOfCommunity().has_object_permission(request, view, obj)
                    or IsLeaderOfBaseCommunity().has_object_permission(request, view, obj)) \
                   and IsDeletableCommunityEvent().has_object_permission(request, view, obj)
        return False


class IsAbleToUpdateLab(permissions.BasePermission):
    ''' Main permission of PUT, PATCH request of Lab '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Lab):
            return IsLecturer().has_permission(request, view) \
                   and IsDeputyLeaderOfCommunity().has_object_permission(request, view, obj)
        return False


class IsAbleToDeleteLab(permissions.BasePermission):
    ''' Main permission of DELETE request of Lab '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Lab):
            return IsLecturer().has_permission(request, view) \
                   and IsLeaderOfCommunity().has_object_permission(request, view, obj) \
                   and IsDeletableLab().has_object_permission(request, view, obj)
        return False


class IsPubliclyVisibleCommunity(permissions.BasePermission):
    ''' Community viewing availability permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, CommunityEvent):
            return request.user.is_authenticated or (obj.is_publicly_visible and obj.created_under.is_publicly_visible)
        elif isinstance(obj, Community):
            return request.user.is_authenticated or obj.is_publicly_visible
        return False


class IsLeaderOfBaseCommunity(permissions.BasePermission):
    ''' Leader of base community permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, CommunityEvent):
            base_community = Community.objects.get(pk=obj.created_under.id)
            base_membership = Membership.objects.filter(
                user_id=request.user.id, position=3, community_id=base_community.id, status__in=('A', 'R')
            )

            return len(base_membership) == 1
        return False


class IsDeputyLeaderOfBaseCommunity(permissions.BasePermission):
    ''' Deputy leader of base community permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, CommunityEvent):
            base_community = Community.objects.get(pk=obj.created_under.id)
            base_membership = Membership.objects.filter(
                user_id=request.user.id, position__in=(2, 3), community_id=base_community.id, status__in=('A', 'R')
            )

            return len(base_membership) == 1
        return False


class IsStaffOfBaseCommunity(permissions.BasePermission):
    ''' Staff of base community permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, CommunityEvent):
            base_community = Community.objects.get(pk=obj.created_under.id)
            base_membership = Membership.objects.filter(
                user_id=request.user.id, position__in=(1, 2, 3), community_id=base_community.id, status__in=('A', 'R')
            )

            return len(base_membership) == 1
        return False


class IsMemberOfBaseCommunity(permissions.BasePermission):
    ''' Member of base community permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, CommunityEvent):
            base_community = Community.objects.get(pk=obj.created_under.id)
            base_membership = Membership.objects.filter(
                user_id=request.user.id, community_id=base_community.id, status__in=('A', 'R')
            )

            return len(base_membership) == 1
        return False


class IsRenewableClub(permissions.BasePermission):
    ''' Renewable club permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Club):
            return not obj.is_official or obj.valid_through is None \
                   or datetime.now().date() >= (obj.valid_through - CLUB_ADVANCED_RENEWAL)
        return False


class IsDeletableClub(permissions.BasePermission):
    ''' Deletable club permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Club):
            return not obj.is_official
        return False


class IsDeletableEvent(permissions.BasePermission):
    ''' Deletable event permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Event):
            return not obj.is_approved
        return False


# TODO: Implements a better deletable condition
class IsDeletableCommunityEvent(permissions.BasePermission):
    ''' Deletable community event permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, CommunityEvent):
            return True
        return False


# TODO: Implements a better deletable condition
class IsDeletableLab(permissions.BasePermission):
    ''' Deletable lab permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Lab):
            return True
        return False
