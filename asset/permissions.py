from rest_framework import permissions

from asset.models import Announcement, Album, Comment, AlbumImage
from community.models import Community


class IsInPubliclyVisibleCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Announcement, Album, AlbumImage, Comment
        if isinstance(obj, (Announcement, Album)):
            return request.user.is_authenticated or Community.objects.get(pk=obj.community.id).is_publicly_visible
        elif isinstance(obj, AlbumImage):
            return request.user.is_authenticated or Community.objects.get(pk=obj.album.community.id).is_publicly_visible
        elif isinstance(obj, Comment):
            return request.user.is_authenticated or Community.objects.get(pk=obj.event.id).is_publicly_visible
        return False
