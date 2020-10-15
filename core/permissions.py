from rest_framework import permissions

from asset.models import Announcement, Album, AlbumImage, Comment
from community.models import Community
from generator.models import QRCode, JoinKey
from membership.models import Request, Invitation, Advisory, Membership, CustomMembershipLabel, MembershipLog
from membership.models import ApprovalRequest


class IsInPubliclyVisibleCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object classes: Announcement, Album, AlbumImage, Comment, Request, Invitation, Advisory,
        #                 Membership, CustomMembershipLabel, MembershipLog, ApprovalRequest, QRCode, JoinKey
        if isinstance(obj, (Announcement, Album, Request, Invitation, Advisory, Membership, ApprovalRequest, QRCode)):
            ref = obj.community.id
        elif isinstance(obj, AlbumImage):
            ref = obj.album.community.id
        elif isinstance(obj, (Comment, JoinKey)):
            ref = obj.event.id
        elif isinstance(obj, (CustomMembershipLabel, MembershipLog)):
            ref = obj.membership.community.id
        else:
            return False

        return request.user.is_authenticated or Community.objects.get(pk=ref).is_publicly_visible


class IsLeaderOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object classes: Community, Announcement, Album, AlbumImage, Comment, Request, Invitation, Advisory,
        #                 Membership, CustomMembershipLabel, MembershipLog, ApprovalRequest, QRCode, JoinKey
        if isinstance(obj, Community):
            ref = obj.id
        elif isinstance(obj, (Announcement, Album, Request, Invitation, Advisory, Membership, ApprovalRequest, QRCode)):
            ref = obj.community.id
        elif isinstance(obj, AlbumImage):
            ref = obj.album.community.id
        elif isinstance(obj, (Comment, JoinKey)):
            ref = obj.event.id
        elif isinstance(obj, (CustomMembershipLabel, MembershipLog)):
            ref = obj.membership.community.id
        else:
            return False

        membership = Membership.objects.filter(
            user_id=request.user.id, position=3, community_id=ref, status='A'
        )
        return len(membership) == 1


class IsDeputyLeaderOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object classes: Community, Announcement, Album, AlbumImage, Comment, Request, Invitation, Advisory,
        #                 Membership, CustomMembershipLabel, MembershipLog, ApprovalRequest, QRCode, JoinKey
        if isinstance(obj, Community):
            ref = obj.id
        elif isinstance(obj, (Announcement, Album, Request, Invitation, Advisory, Membership, ApprovalRequest, QRCode)):
            ref = obj.community.id
        elif isinstance(obj, AlbumImage):
            ref = obj.album.community.id
        elif isinstance(obj, (Comment, JoinKey)):
            ref = obj.event.id
        elif isinstance(obj, (CustomMembershipLabel, MembershipLog)):
            ref = obj.membership.community.id
        else:
            return False

        membership = Membership.objects.filter(
            user_id=request.user.id, position__in=(2, 3), community_id=ref, status='A'
        )
        return len(membership) == 1


class IsStaffOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object classes: Community, Announcement, Album, AlbumImage, Comment, Request, Invitation, Advisory,
        #                 Membership, CustomMembershipLabel, MembershipLog, ApprovalRequest, QRCode, JoinKey
        if isinstance(obj, Community):
            ref = obj.id
        elif isinstance(obj, (Announcement, Album, Request, Invitation, Advisory, Membership, ApprovalRequest, QRCode)):
            ref = obj.community.id
        elif isinstance(obj, AlbumImage):
            ref = obj.album.community.id
        elif isinstance(obj, (Comment, JoinKey)):
            ref = obj.event.id
        elif isinstance(obj, (CustomMembershipLabel, MembershipLog)):
            ref = obj.membership.community.id
        else:
            return False

        membership = Membership.objects.filter(
            user_id=request.user.id, position__in=(1, 2, 3), community_id=ref, status='A'
        )
        return len(membership) == 1


class IsMemberOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object classes: Community, Announcement, Album, AlbumImage, Comment, Request, Invitation, Advisory,
        #                 Membership, CustomMembershipLabel, MembershipLog, ApprovalRequest, QRCode, JoinKey
        if isinstance(obj, Community):
            ref = obj.id
        elif isinstance(obj, (Announcement, Album, Request, Invitation, Advisory, Membership, ApprovalRequest, QRCode)):
            ref = obj.community.id
        elif isinstance(obj, AlbumImage):
            ref = obj.album.community.id
        elif isinstance(obj, (Comment, JoinKey)):
            ref = obj.event.id
        elif isinstance(obj, (CustomMembershipLabel, MembershipLog)):
            ref = obj.membership.community.id
        else:
            return False

        membership = Membership.objects.filter(user_id=request.user.id, community_id=ref, status__in=('A', 'R'))

        return len(membership) == 1
