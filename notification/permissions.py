from rest_framework import permissions


class IsNotificationOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Notification
        return request.user.id == obj.user.id
