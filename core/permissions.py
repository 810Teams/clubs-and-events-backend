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
from misc.models import Vote
from notification.models import Notification, RequestNotification, MembershipLogNotification, AnnouncementNotification
from notification.models import CommunityEventNotification, EventNotification


class IsInPubliclyVisibleCommunity(permissions.BasePermission):
    ''' Items viewing availability permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        ref = get_community_reference(obj)

        if ref is not None:
            community = Community.objects.get(pk=ref.id)
            if request.user.is_authenticated:
                return True
            elif has_instance(community, CommunityEvent):
                community_event = CommunityEvent.objects.get(pk=community.id)
                return community_event.is_publicly_visible and community_event.created_under.is_publicly_visible
            return community.is_publicly_visible
        return False


class IsInActiveCommunity(permissions.BasePermission):
    ''' Permission for checking if the object is in or related to an active community '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        ref = get_community_reference(obj)
        if ref is not None:
            return ref.is_active
        return False


class IsLeaderOfCommunity(permissions.BasePermission):
    ''' Leader of community permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        ref = get_community_reference(obj)

        if ref is not None:
            membership = Membership.objects.filter(user_id=request.user.id, position=3, community_id=ref.id, status='A')
            return len(membership) == 1
        return False


class IsDeputyLeaderOfCommunity(permissions.BasePermission):
    ''' Deputy leader of community permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        ref = get_community_reference(obj)

        if ref is not None:
            membership = Membership.objects.filter(
                user_id=request.user.id, position__in=(2, 3), community_id=ref.id, status='A'
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
                user_id=request.user.id, position__in=(1, 2, 3), community_id=ref.id, status='A'
            )
            return len(membership) == 1
        return False


class IsMemberOfCommunity(permissions.BasePermission):
    ''' Member of community permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        ref = get_community_reference(obj)

        if ref is not None:
            membership = Membership.objects.filter(user_id=request.user.id, community_id=ref.id, status__in=('A', 'R'))
            return len(membership) == 1
        return False


def get_community_reference(obj):
    ''' Retrieve a reference to community from an object '''
    if isinstance(obj, Community):
        return obj
    elif isinstance(obj, (Announcement, Album, Request, Invitation, Advisory, Membership, ApprovalRequest)):
        return obj.community
    elif isinstance(obj, AlbumImage):
        return obj.album.community
    elif isinstance(obj, (Comment, QRCode, JoinKey)):
        return obj.event
    elif isinstance(obj, (CustomMembershipLabel, MembershipLog)):
        return obj.membership.community
    elif isinstance(obj, GeneratedDocx):
        return obj.club
    elif isinstance(obj, Vote):
        return obj.voted_for.community
    elif isinstance(obj, Notification):
        if has_instance(obj, RequestNotification):
            return get_community_reference(RequestNotification.objects.get(pk=obj.id).request)
        elif has_instance(obj, MembershipLogNotification):
            return get_community_reference(MembershipLogNotification.objects.get(pk=obj.id).membership_log)
        elif has_instance(obj, AnnouncementNotification):
            return get_community_reference(AnnouncementNotification.objects.get(pk=obj.id).announcement)
        elif has_instance(obj, CommunityEventNotification):
            return get_community_reference(CommunityEventNotification.objects.get(pk=obj.id).community_event)
        elif has_instance(obj, EventNotification):
            return get_community_reference(EventNotification.objects.get(pk=obj.id).event)
        else:
            return None
    return None
