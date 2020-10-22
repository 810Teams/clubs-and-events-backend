'''
    Notification Application Permissions
    notification/permissions.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import permissions

from notification.models import Notification


class IsNotificationOwner(permissions.BasePermission):
    ''' Notification owner permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Notification):
            return request.user.id == obj.user.id
        return False
