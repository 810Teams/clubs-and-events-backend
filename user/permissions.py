from datetime import datetime
from rest_framework import permissions

from user.models import StudentCommitteeAuthority


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_lecturer


class IsLecturer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_lecturer


class IsStudentCommittee(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            authority = StudentCommitteeAuthority.objects.get(pk=request.user.id)
            return authority.start_date <= datetime.now().date() <= authority.end_date
        except StudentCommitteeAuthority.DoesNotExist:
            return False


class IsProfileOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: User
        return request.user.id == obj.id


class IsEmailPreferenceOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object class: Email Preference
        return request.user.id == obj.user.id
