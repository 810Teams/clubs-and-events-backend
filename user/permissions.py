from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='student').exists()


class IsLecturer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='lecturer').exists()
