'''
    Asset Application Permissions
    asset/permissions.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import permissions

from asset.models import Announcement, Comment, Album
from core.permissions import IsInPubliclyVisibleCommunity, IsMemberOfCommunity, IsDeputyLeaderOfCommunity


class IsAbleToRetrieveAnnouncement(permissions.BasePermission):
    ''' Main permission of GET request of Announcement '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Announcement):
            if IsMemberOfCommunity().has_object_permission(request, view, obj):
                return True
            elif IsInPubliclyVisibleCommunity().has_object_permission(request, view, obj) and obj.is_publicly_visible:
                return True
        return False


class IsAbleToRetrieveAlbum(permissions.BasePermission):
    ''' Main permission of GET request of Announcement '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Album):
            if IsMemberOfCommunity().has_object_permission(request, view, obj):
                return True
            elif IsInPubliclyVisibleCommunity().has_object_permission(request, view, obj) and obj.is_publicly_visible:
                return True
        return False


class IsAbleToDeleteComment(permissions.BasePermission):
    ''' Main permission of DELETE request of Comment '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Comment):
            if obj.created_by is not None and obj.created_by.id == request.user.id:
                return True
            elif IsDeputyLeaderOfCommunity().has_object_permission(request, view, obj):
                return True
        return False
