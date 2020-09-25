from rest_framework import permissions

from community.models import Community


class IsInPubliclyVisibleCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Announcement, Album
        if not request.user.is_authenticated and not Community.objects.get(pk=obj.community.id).is_publicly_visible:
            return False
        return True


class IsInPubliclyVisibleEvent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Comment
        if not request.user.is_authenticated and not Community.objects.get(pk=obj.event.id).is_publicly_visible:
            return False
        return True
