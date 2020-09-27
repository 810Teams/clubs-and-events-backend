from rest_framework import permissions

from asset.models import Announcement, Album, AlbumImage, Comment
from community.models import Community
from membership.models import Request, Invitation, Advisory, Membership


class IsLeaderOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Community, Announcement, Album, AlbumImage, Request, Invitation, Advisory, Membership
        if isinstance(obj, Community):
            ref = obj.id
        elif isinstance(obj, (Announcement, Album, Request, Invitation, Advisory, Membership)):
            ref = obj.community.id
        elif isinstance(obj, AlbumImage):
            ref = obj.album.community.id
        else:
            return False

        membership = Membership.objects.filter(
            user_id=request.user.id, position__in=[3], community_id=ref, status='A'
        )
        return len(membership) == 1


class IsDeputyLeaderOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Community, Announcement, Album, AlbumImage, Request, Invitation, Advisory, Membership
        if isinstance(obj, Community):
            ref = obj.id
        elif isinstance(obj, (Announcement, Album, Request, Invitation, Advisory, Membership)):
            ref = obj.community.id
        elif isinstance(obj, AlbumImage):
            ref = obj.album.community.id
        else:
            return False

        membership = Membership.objects.filter(
            user_id=request.user.id, position__in=[2, 3], community_id=ref, status='A'
        )
        return len(membership) == 1


class IsStaffOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Community, Announcement, Album, AlbumImage, Request, Invitation, Advisory, Membership
        if isinstance(obj, Community):
            ref = obj.id
        elif isinstance(obj, (Announcement, Album, Request, Invitation, Advisory, Membership)):
            ref = obj.community.id
        elif isinstance(obj, AlbumImage):
            ref = obj.album.community.id
        else:
            return False

        membership = Membership.objects.filter(
            user_id=request.user.id, position__in=[1, 2, 3], community_id=ref, status='A'
        )
        return len(membership) == 1


class IsMemberOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Community, Announcement, Album, AlbumImage, Request, Invitation, Advisory, Membership
        if isinstance(obj, Community):
            ref = obj.id
        elif isinstance(obj, (Announcement, Album, Request, Invitation, Advisory, Membership)):
            ref = obj.community.id
        elif isinstance(obj, AlbumImage):
            ref = obj.album.community.id
        else:
            return False

        membership = Membership.objects.filter(user_id=request.user.id, community_id=ref, status='A')

        return len(membership) == 1


class IsNotMemberOfCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Community, Announcement, Album, AlbumImage, Request, Invitation, Advisory, Membership
        if isinstance(obj, Community):
            ref = obj.id
        elif isinstance(obj, (Announcement, Album, Request, Invitation, Advisory, Membership)):
            ref = obj.community.id
        elif isinstance(obj, AlbumImage):
            ref = obj.album.community.id
        else:
            return False

        membership = Membership.objects.filter(user_id=request.user.id, community_id=ref, status='A')

        return len(membership) == 0
