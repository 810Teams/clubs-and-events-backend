'''
    Asset Application Permissions
    asset/permissions.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import permissions

from asset.models import Announcement
from core.permissions import IsInPubliclyVisibleCommunity, IsMemberOfCommunity


class IsAbleToRetrieveAnnouncement(permissions.BasePermission):
    ''' Main permission of GET request of Announcement '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Announcement):
            if obj.is_publicly_visible and IsInPubliclyVisibleCommunity().has_object_permission(request, view, obj):
                return True
            elif not obj.is_publicly_visible and IsMemberOfCommunity().has_object_permission(request, view, obj):
                return True
        return False
