'''
    Core Application Permissions
    core/permissions.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import permissions

from asset.models import Announcement, Album, AlbumImage, Comment
from community.models import Community, CommunityEvent
from core.utils.general import has_instance
from generator.models import QRCode, JoinKey, GeneratedDocx
from membership.models import Request, Invitation, Advisory, Membership, CustomMembershipLabel, MembershipLog
from membership.models import ApprovalRequest


class IsInPubliclyVisibleCommunity(permissions.BasePermission):
    ''' Items viewing availability permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        ref = get_community_reference(obj)

        if ref is not None:
            community = Community.objects.get(pk=ref)
            if request.user.is_authenticated:
                return True
            elif has_instance(community, CommunityEvent):
                community_event = CommunityEvent.objects.get(pk=community.id)
                return community_event.is_publicly_visible and community_event.created_under.is_publicly_visible
            return community.is_publicly_visible
        return False


class IsLeaderOfCommunity(permissions.BasePermission):
    ''' Leader of community permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        ref = get_community_reference(obj)

        if ref is not None:
            membership = Membership.objects.filter(user_id=request.user.id, position=3, community_id=ref, status='A')
            return len(membership) == 1
        return False


class IsDeputyLeaderOfCommunity(permissions.BasePermission):
    ''' Deputy leader of community permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        ref = get_community_reference(obj)

        if ref is not None:
            membership = Membership.objects.filter(
                user_id=request.user.id, position__in=(2, 3), community_id=ref, status='A'
            )
            return len(membership) == 1
        return False


class IsStaffOfCommunity(permissions.BasePermission):
    ''' Staff of community permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        ref = get_community_reference(obj)

        if ref is not None:
            membership = Membership.objects.filter(
                user_id=request.user.id, position__in=(1, 2, 3), community_id=ref, status='A'
            )
            return len(membership) == 1
        return False


class IsMemberOfCommunity(permissions.BasePermission):
    ''' Member of community permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        ref = get_community_reference(obj)

        if ref is not None:
            membership = Membership.objects.filter(user_id=request.user.id, community_id=ref, status__in=('A', 'R'))
            return len(membership) == 1
        return False


def get_community_reference(obj):
    ''' Retrieve a reference to community from an object '''
    if isinstance(obj, Community):
        return obj.id
    elif isinstance(obj, (Announcement, Album, Request, Invitation, Advisory, Membership, ApprovalRequest)):
        return obj.community.id
    elif isinstance(obj, AlbumImage):
        return obj.album.community.id
    elif isinstance(obj, (Comment, QRCode, JoinKey)):
        return obj.event.id
    elif isinstance(obj, (CustomMembershipLabel, MembershipLog)):
        return obj.membership.community.id
    elif isinstance(obj, GeneratedDocx):
        return obj.club.id
    return None
