'''
    User Application Permissions
    user/permissions.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import permissions

from user.models import StudentCommitteeAuthority, EmailPreference


class IsStudent(permissions.BasePermission):
    ''' Student permission '''
    def has_permission(self, request, view):
        ''' Check permission on request '''
        if request.user.is_authenticated:
            return request.user.user_group == 'student'
        return False


class IsLecturer(permissions.BasePermission):
    ''' Lecturer permission '''
    def has_permission(self, request, view):
        ''' Check permission on request '''
        if request.user.is_authenticated:
            return request.user.user_group == 'lecturer'
        return False


class IsSupportStaff(permissions.BasePermission):
    ''' Lecturer permission '''
    def has_permission(self, request, view):
        ''' Check permission on request '''
        if request.user.is_authenticated:
            return request.user.user_group == 'support'
        return False


class IsStudentObject(permissions.BasePermission):
    ''' Student object permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, get_user_model()):
            return obj.user_group == 'student'
        return False


class IsLecturerObject(permissions.BasePermission):
    ''' Lecturer object permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, get_user_model()):
            return obj.user_group == 'lecturer'
        return False


class IsSupportStaffObject(permissions.BasePermission):
    ''' Support staff object permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, get_user_model()):
            return obj.user_group == 'support'
        return False


class IsStudentCommittee(permissions.BasePermission):
    ''' Student committee member permission '''
    def has_permission(self, request, view):
        ''' Check permission on request '''
        try:
            authority = StudentCommitteeAuthority.objects.get(user_id=request.user.id)
            return authority.start_date <= datetime.now().date() <= authority.end_date
        except StudentCommitteeAuthority.DoesNotExist:
            return False


class IsProfileOwner(permissions.BasePermission):
    ''' Profile owner permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, get_user_model()):
            return request.user.id == obj.id
        return False


class IsEmailPreferenceOwner(permissions.BasePermission):
    ''' Email preference owner permission '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, EmailPreference):
            return request.user.id == obj.user.id
        return False
