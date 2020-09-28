from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='student').exists()


class IsLecturer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='lecturer').exists()


class IsProfileOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: User
        return request.user.id == obj.id


class IsEmailPreferenceOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Email Preference
        return request.user.id == obj.user.id
