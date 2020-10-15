from rest_framework import permissions

from core.permissions import IsStaffOfCommunity, IsMemberOfCommunity, IsDeputyLeaderOfCommunity, IsLeaderOfCommunity
from user.permissions import IsStudentCommittee


class IsAbleToRetrieveRequest(permissions.BasePermission):
    ''' Main permission of GET request of Request '''
    def has_object_permission(self, request, view, obj):
        return IsMemberOfCommunity().has_object_permission(request, view, obj) and request.user.id == obj.user.id


class IsAbleToUpdateRequest(permissions.BasePermission):
    ''' Main permission of PUT, PATCH request of Request '''
    def has_object_permission(self, request, view, obj):
        return IsStaffOfCommunity().has_object_permission(request, view, obj) and obj.status == 'W'


class IsAbleToDeleteRequest(permissions.BasePermission):
    ''' Main permission of DELETE request of Request '''
    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.user.id and obj.status == 'W'


class IsAbleToRetrieveInvitation(permissions.BasePermission):
    ''' Main permission of GET request of Invitation '''
    def has_object_permission(self, request, view, obj):
        return IsMemberOfCommunity().has_object_permission(request, view, obj) and request.user.id == obj.invitee.id


class IsAbleToUpdateInvitation(permissions.BasePermission):
    ''' Main permission of PUT, PATCH request of Invitation '''
    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.invitee.id and obj.status == 'W'


class IsAbleToDeleteInvitation(permissions.BasePermission):
    ''' Main permission of DELETE request of Invitation '''
    def has_object_permission(self, request, view, obj):
        if obj.status != 'W':
            return False
        if request.user.id == obj.invitor:
            return True

        return IsDeputyLeaderOfCommunity().has_object_permission(request, view, obj)


class IsAbleToUpdateMembership(permissions.BasePermission):
    ''' Main permission of PUT, PATCH request of Membership '''
    def has_object_permission(self, request, view, obj):
        # Prerequisite 1: Memberships with a status of 'L' or 'X' are not able to be updated
        if obj.status in ('L', 'X'):
            return False

        # Prerequisite 2: Memberships with a position of 3 are not able to be updated
        if obj.position == 3:
            return False

        # Case 1: Leaving and retiring, must be the membership owner.
        is_membership_owner = request.user.id == obj.user.id and obj.position not in ('L', 'X')

        # Case 2: Member removal and position assignation, must be done by an active deputy leader of the community,
        #         and not be done on memberships with position equal to yourself.
        is_deputy_leader_of_that_community = IsDeputyLeaderOfCommunity().has_object_permission(request, view, obj)

        return is_membership_owner or is_deputy_leader_of_that_community


class IsAbleToUpdateCustomMembershipLabel(permissions.BasePermission):
    ''' Main permission of PUT, PATCH request of CustomMembershipLabel '''
    def has_object_permission(self, request, view, obj):
        return IsDeputyLeaderOfCommunity().has_object_permission(request, view, obj) \
               and obj.membership.position in (1, 2)


class IsAbleToRetrieveApprovalRequest(permissions.BasePermission):
    ''' Main permission of GET request of ApprovalRequest '''
    def has_object_permission(self, request, view, obj):
        return IsLeaderOfCommunity().has_object_permission(request, view, obj) \
               or IsStudentCommittee().has_object_permission(request, view, obj)


class IsAbleToUpdateApprovalRequest(permissions.BasePermission):
    ''' Main permission of PUT, PATCH request of ApprovalRequest '''
    def has_object_permission(self, request, view, obj):
        return IsStudentCommittee().has_object_permission(request, view, obj) and obj.status == 'W'


class IsAbleToDeleteApprovalRequest(permissions.BasePermission):
    ''' Main permission of DELETE request of ApprovalRequest '''
    def has_object_permission(self, request, view, obj):
        return IsLeaderOfCommunity().has_object_permission(request, view, obj) and obj.status == 'W'
