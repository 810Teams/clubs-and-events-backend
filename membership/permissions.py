'''
    Membership Application Permissions
    membership/permissions.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import permissions

from core.permissions import IsStaffOfCommunity, IsMemberOfCommunity, IsDeputyLeaderOfCommunity, IsLeaderOfCommunity
from membership.models import Request, Invitation, Membership, CustomMembershipLabel, ApprovalRequest, Advisory
from user.permissions import IsStudentCommittee, IsSupportStaff


class IsAbleToRetrieveRequest(permissions.BasePermission):
    ''' Main permission of GET request of Request '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Request):
            return IsMemberOfCommunity().has_object_permission(request, view, obj) or request.user.id == obj.user.id
        return False


class IsAbleToUpdateRequest(permissions.BasePermission):
    ''' Main permission of PUT, PATCH request of Request '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Request):
            return IsStaffOfCommunity().has_object_permission(request, view, obj) and obj.status == 'W'
        return False


class IsAbleToDeleteRequest(permissions.BasePermission):
    ''' Main permission of DELETE request of Request '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Request):
            return request.user.id == obj.user.id and obj.status == 'W'
        return False


class IsAbleToRetrieveInvitation(permissions.BasePermission):
    ''' Main permission of GET request of Invitation '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Invitation):
            return IsMemberOfCommunity().has_object_permission(request, view, obj) or request.user.id == obj.invitee.id
        return False


class IsAbleToUpdateInvitation(permissions.BasePermission):
    ''' Main permission of PUT, PATCH request of Invitation '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Invitation):
            return request.user.id == obj.invitee.id and obj.status == 'W'
        return False


class IsAbleToDeleteInvitation(permissions.BasePermission):
    ''' Main permission of DELETE request of Invitation '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Invitation):
            if obj.status != 'W':
                return False
            if request.user.id == obj.invitor:
                return True

            return IsDeputyLeaderOfCommunity().has_object_permission(request, view, obj)
        return False


class IsAbleToUpdateMembership(permissions.BasePermission):
    ''' Main permission of PUT, PATCH request of Membership '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Membership):
            # Prerequisite 1: Memberships with a status of 'L' or 'X' are not able to be updated
            if obj.status in ('L', 'X'):
                return False

            # Prerequisite 2: Memberships with a position of 3 are not able to be updated
            if obj.position == 3:
                return False

            # Case 1: Leaving and retiring, must be the membership owner.
            is_membership_owner = request.user.id == obj.user.id

            # Case 2: Member removal and position assignation must be done by an active deputy leader of the community,
            #         and not be done on memberships with position equal to yourself.
            is_deputy_leader = IsDeputyLeaderOfCommunity().has_object_permission(request, view, obj)

            return is_membership_owner or is_deputy_leader
        return False


class IsAbleToUpdateCustomMembershipLabel(permissions.BasePermission):
    ''' Main permission of PUT, PATCH request of CustomMembershipLabel '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, CustomMembershipLabel):
            return IsDeputyLeaderOfCommunity().has_object_permission(request, view, obj) \
                   and obj.membership.position in (1, 2)
        return False


class IsAbleToCreateAndDeleteAdvisory(permissions.BasePermission):
    ''' Main permission of POST, DELETE request of Advisory '''
    def has_permission(self, request, view):
        ''' Check permission on request '''
        return IsStudentCommittee().has_permission(request, view) \
               or IsSupportStaff().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, Advisory):
            return IsStudentCommittee().has_permission(request, view) \
                   or IsSupportStaff().has_permission(request, view)
        return False


class IsAbleToRetrieveApprovalRequest(permissions.BasePermission):
    ''' Main permission of GET request of ApprovalRequest '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, ApprovalRequest):
            return IsLeaderOfCommunity().has_object_permission(request, view, obj) \
                   or IsStudentCommittee().has_permission(request, view) \
                   or IsSupportStaff().has_permission(request, view)
        return False


class IsAbleToUpdateApprovalRequest(permissions.BasePermission):
    ''' Main permission of PUT, PATCH request of ApprovalRequest '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, ApprovalRequest):
            return (IsStudentCommittee().has_permission(request, view)
                    or IsSupportStaff().has_permission(request, view)) \
                   and obj.status == 'W'
        return False


class IsAbleToDeleteApprovalRequest(permissions.BasePermission):
    ''' Main permission of DELETE request of ApprovalRequest '''
    def has_object_permission(self, request, view, obj):
        ''' Check permission on object '''
        if isinstance(obj, ApprovalRequest):
            return IsLeaderOfCommunity().has_object_permission(request, view, obj) and obj.status == 'W'
        return False
