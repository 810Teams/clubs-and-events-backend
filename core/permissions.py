from rest_framework import permissions

from asset.models import Announcement, Album, AlbumImage, Comment
from community.models import Community
from generator.models import QRCode, JoinKey, GeneratedDocx
from membership.models import Request, Invitation, Advisory, Membership, CustomMembershipLabel, MembershipLog
from membership.models import ApprovalRequest


class IsInPubliclyVisibleCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object classes: Community, Announcement, Album, AlbumImage, Comment, Request, Invitation, Advisory,
        #                 Membership, CustomMembershipLabel, MembershipLog, ApprovalRequest, QRCode, JoinKey
        #                 GeneratedDocx
        ref = get_community_reference(obj)

        return request.user.is_authenticated or Community.objects.get(pk=ref).is_publicly_visible


class IsLeaderOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object classes: Community, Announcement, Album, AlbumImage, Comment, Request, Invitation, Advisory,
        #                 Membership, CustomMembershipLabel, MembershipLog, ApprovalRequest, QRCode, JoinKey,
        #                 GeneratedDocx
        ref = get_community_reference(obj)

        membership = Membership.objects.filter(
            user_id=request.user.id, position=3, community_id=ref, status='A'
        )
        return len(membership) == 1


class IsDeputyLeaderOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object classes: Community, Announcement, Album, AlbumImage, Comment, Request, Invitation, Advisory,
        #                 Membership, CustomMembershipLabel, MembershipLog, ApprovalRequest, QRCode, JoinKey
        #                 GeneratedDocx
        ref = get_community_reference(obj)

        membership = Membership.objects.filter(
            user_id=request.user.id, position__in=(2, 3), community_id=ref, status='A'
        )
        return len(membership) == 1


class IsStaffOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object classes: Community, Announcement, Album, AlbumImage, Comment, Request, Invitation, Advisory,
        #                 Membership, CustomMembershipLabel, MembershipLog, ApprovalRequest, QRCode, JoinKey
        #                 GeneratedDocx
        ref = get_community_reference(obj)

        membership = Membership.objects.filter(
            user_id=request.user.id, position__in=(1, 2, 3), community_id=ref, status='A'
        )
        return len(membership) == 1


class IsMemberOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object classes: Community, Announcement, Album, AlbumImage, Comment, Request, Invitation, Advisory,
        #                 Membership, CustomMembershipLabel, MembershipLog, ApprovalRequest, QRCode, JoinKey
        #                 GeneratedDocx
        ref = get_community_reference(obj)

        membership = Membership.objects.filter(user_id=request.user.id, community_id=ref, status__in=('A', 'R'))

        return len(membership) == 1


def get_community_reference(obj):
    if isinstance(obj, Community):
        return obj.id
    elif isinstance(obj, (Announcement, Album, Request, Invitation, Advisory, Membership, ApprovalRequest, QRCode)):
        return obj.community.id
    elif isinstance(obj, AlbumImage):
        return obj.album.community.id
    elif isinstance(obj, (Comment, JoinKey)):
        return  obj.event.id
    elif isinstance(obj, (CustomMembershipLabel, MembershipLog)):
        return obj.membership.community.id
    elif isinstance(obj, GeneratedDocx):
        return obj.club.id
    return None
