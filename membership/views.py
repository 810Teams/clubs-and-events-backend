from datetime import datetime

from django.utils.translation import gettext as _
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from community.models import CommunityEvent, Community, Club, Event, Lab
from core.permissions import IsStaffOfCommunity, IsDeputyLeaderOfCommunity, IsLeaderOfCommunity
from core.permissions import IsInPubliclyVisibleCommunity
from core.utils import filter_queryset
from membership.models import Request, Membership, Invitation, CustomMembershipLabel, Advisory, MembershipLog
from membership.models import ApprovalRequest
from membership.permissions import IsRequestOwner, IsWaitingRequest, IsAbleToViewRequestList
from membership.permissions import IsWaitingInvitation, IsAbleToViewApprovalRequestList, IsWaitingApprovalRequest
from membership.permissions import IsInvitationInvitee, IsAbleToCancelInvitation, IsAbleToViewInvitationList
from membership.permissions import IsAbleToUpdateMembership, IsApplicableForCustomMembershipLabel
from membership.serializers import ExistingRequestSerializer, NotExistingRequestSerializer, MembershipLogSerializer
from membership.serializers import NotExistingApprovalRequestSerializer, ExistingApprovalRequestSerializer
from membership.serializers import ExistingInvitationSerializer, NotExistingInvitationSerializer
from membership.serializers import MembershipSerializer, AdvisorySerializer
from membership.serializers import NotExistingCustomMembershipLabelSerializer, ExistingCustomMembershipLabelSerializer
from notification.notifier import notify
from user.models import StudentCommitteeAuthority
from user.permissions import IsStudentCommittee


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (permissions.IsAuthenticated(), IsAbleToViewRequestList())
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsStaffOfCommunity(), IsWaitingRequest())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsRequestOwner(), IsWaitingRequest())
        return tuple()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotExistingRequestSerializer
        return ExistingRequestSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        memberships = Membership.objects.filter(user_id=request.user.id, status__in=('A', 'R'))
        communities = [i.community.id for i in memberships]

        id_set = [i.id for i in queryset.filter(community_id__in=communities)]
        id_set += [i.id for i in queryset.filter(user_id=request.user.id)]

        queryset = queryset.filter(pk__in=id_set)

        queryset = filter_queryset(queryset, request, target_param='user', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # In case of requesting to join the community event, if already a member of the base community,
        # you can join without waiting to be approved.
        try:
            community_event = CommunityEvent.objects.get(pk=obj.community.id)
            Membership.objects.get(
                user_id=request.user.id, community_id=community_event.created_under.id, status__in=('A', 'R')
            )

            request_obj = Request.objects.get(pk=obj.id)
            request_obj.status = 'A'
            request_obj.save()
            Membership.objects.create(user_id=obj.user.id, position=0, community_id=obj.community.id,
                                      created_by_id=request.user.id, updated_by_id=request.user.id)
        except (CommunityEvent.DoesNotExist, Membership.DoesNotExist):
            pass

        # Notification
        users = [i.user for i in Membership.objects.filter(
            community_id=obj.community.id, position__in=(1, 2, 3), status='A'
        )]
        notify(users=users, obj=obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # If the request is accepted, check for past membership to renew it. Otherwise, create a new one.
        if obj.status == 'A':
            try:
                membership = Membership.objects.get(user_id=obj.user.id, community_id=obj.community.id)
                membership.position = 0
                membership.status = 'A'
                membership.save()
            except Membership.DoesNotExist:
                Membership.objects.create(user_id=obj.user.id, community_id=obj.community.id)

        return Response(serializer.data, status=status.HTTP_200_OK)


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (permissions.IsAuthenticated(), IsAbleToViewInvitationList())
        elif self.request.method == 'POST':
            # Includes IsStaffOfCommunity() in validation() of the serializer
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsInvitationInvitee(), IsWaitingInvitation())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsAbleToCancelInvitation())
        return tuple()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotExistingInvitationSerializer
        return ExistingInvitationSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        memberships = Membership.objects.filter(user_id=request.user.id, status__in=('A', 'R'))
        communities = [i.community.id for i in memberships]

        id_set = [i.id for i in queryset.filter(community_id__in=communities)]
        id_set += [i.id for i in queryset.filter(invitee_id=request.user.id)]

        queryset = queryset.filter(pk__in=id_set)

        queryset = filter_queryset(queryset, request, target_param='invitor', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='invitee', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # If the invitation is accepted, check for past membership to renew it. Otherwise, create a new one.
        if obj.status == 'A':
            try:
                membership = Membership.objects.get(user_id=obj.invitee.id, community_id=obj.community.id)
                membership.position = 0
                membership.status = 'A'
                membership.save()
            except Membership.DoesNotExist:
                Membership.objects.create(user_id=obj.invitee.id, community_id=obj.community.id)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    http_method_names = ('get', 'put', 'patch', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsInPubliclyVisibleCommunity(),)
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsAbleToUpdateMembership())
        return tuple()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not self.request.user.is_authenticated:
            visible_ids = [i.id for i in Community.objects.filter(is_publicly_visible=True)]
            queryset = queryset.filter(community_id__in=visible_ids)

        queryset = filter_queryset(queryset, request, target_param='user', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='position', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)

        try:
            query = request.query_params.get('community_type')
            if query == 'club':
                club_ids = [i.id for i in Club.objects.all()]
                queryset = queryset.filter(community_id__in=club_ids)
            elif query == 'event':
                community_event_ids = [i.id for i in CommunityEvent.objects.all()]
                event_ids = [i.id for i in Event.objects.all() if i.id not in community_event_ids]
                queryset = queryset.filter(community_id__in=event_ids)
            elif query == 'community_event':
                community_event_ids = [i.id for i in CommunityEvent.objects.all()]
                queryset = queryset.filter(community_id__in=community_event_ids)
            elif query == 'lab':
                lab_ids = [i.id for i in Lab.objects.all()]
                queryset = queryset.filter(community_id__in=lab_ids)
        except ValueError:
            queryset = None

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        old_position = Membership.objects.get(pk=kwargs['pk']).position
        old_status = Membership.objects.get(pk=kwargs['pk']).status

        serializer = self.get_serializer(self.get_object(), data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # If the membership position is updated to 3, demote own position to 2.
        if old_position != obj.position and obj.position == 3:
            membership = Membership.objects.get(
                user_id=request.user.id,
                community_id=Membership.objects.get(pk=kwargs['pk']).community.id
            )
            membership.position = 2
            membership.updated_by = request.user
            membership.save()

        # If the status is set to retired, get demoted to a normal member.
        if old_status != obj.status and obj.status == 'R':
            membership = Membership.objects.get(
                user_id=request.user.id,
                community_id=Membership.objects.get(pk=kwargs['pk']).community.id
            )
            membership.position = 0
            membership.updated_by = request.user
            membership.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomMembershipLabelViewSet(viewsets.ModelViewSet):
    queryset = CustomMembershipLabel.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsInPubliclyVisibleCommunity(),)
        elif self.request.method == 'POST':
            # Includes IsDeputyLeaderOfCommunity() in validate() of the serializer
            # Includes IsApplicableForCustomMembershipLabel() in validate() of the serializer
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsDeputyLeaderOfCommunity(), IsApplicableForCustomMembershipLabel())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsDeputyLeaderOfCommunity())
        return tuple()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotExistingCustomMembershipLabelSerializer
        return ExistingCustomMembershipLabelSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not self.request.user.is_authenticated:
            visible_ids = [i.id for i in Community.objects.filter(is_publicly_visible=True)]
            visible_ids = [i.id for i in Membership.objects.filter(community_id__in=visible_ids)]
            queryset = queryset.filter(membership_id__in=visible_ids)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class AdvisoryViewSet(viewsets.ModelViewSet):
    queryset = Advisory.objects.all()
    serializer_class = AdvisorySerializer
    http_method_names = ('get', 'post', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'POST':
            return (permissions.IsAuthenticated(), IsStudentCommittee())
        return (permissions.IsAuthenticated(),)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = filter_queryset(queryset, request, target_param='advisor', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)

        try:
            query = request.query_params.get('is_active')
            if query is not None:
                query = eval(query)
                active_ids = [i.id for i in queryset if i.start_date <= datetime.now().date() <= i.end_date]

                if query:
                    queryset = queryset.filter(pk__in=active_ids)
                else:
                    queryset = queryset.exclude(pk__in=active_ids)
        except ValueError:
            queryset = None

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class MembershipLogViewSet(viewsets.ModelViewSet):
    queryset = MembershipLog.objects.all()
    serializer_class = MembershipLogSerializer
    http_method_names = ('get', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsInPubliclyVisibleCommunity(),)
        return tuple()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not self.request.user.is_authenticated:
            visible_community_ids = [i.id for i in Community.objects.filter(is_publicly_visible=True)]
            visible_membership_ids = [i.id for i in Membership.objects.filter(community_id__in=visible_community_ids)]
            queryset = queryset.filter(membership_id__in=visible_membership_ids)

        try:
            query = request.query_params.get('user')
            if query is not None:
                membership_ids = [i.id for i in Membership.objects.filter(user_id=query)]
                queryset = queryset.filter(membership_id__in=membership_ids)

            query = request.query_params.get('community')
            if query is not None:
                membership_ids = [i.id for i in Membership.objects.filter(community_id=query)]
                queryset = queryset.filter(membership_id__in=membership_ids)

            query = request.query_params.get('exclude_current_memberships')
            if query is not None:
                if eval(query):
                    queryset = queryset.exclude(end_datetime=None)
        except ValueError:
            queryset = None

        queryset = filter_queryset(queryset, request, target_param='position', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # Notification
        notify(users=[request.user], obj=obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    queryset = ApprovalRequest.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (permissions.IsAuthenticated(), IsAbleToViewApprovalRequestList())
        elif self.request.method == 'POST':
            # Includes IsLeaderOfCommunity() in validate() of the serializer
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsStudentCommittee(), IsWaitingApprovalRequest())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsLeaderOfCommunity(), IsWaitingApprovalRequest())
        return (permissions.IsAuthenticated(),)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotExistingApprovalRequestSerializer
        return ExistingApprovalRequestSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        try:
            authority = StudentCommitteeAuthority.objects.get(user_id=request.user.id)
            is_student_committee = authority.start_date <= datetime.now().date() <= authority.end_date
        except StudentCommitteeAuthority.DoesNotExist:
            is_student_committee = False

        if not is_student_committee:
            visible_ids = [i.community.id for i in Membership.objects.filter(
                user_id=request.user.id, status='A', position=3
            )]
            queryset = queryset.filter(community_id__in=visible_ids)

        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        if obj.status == 'A':
            try:
                club = Club.objects.get(pk=obj.community.id)
                club.is_official = True
                club.save()
            except Club.DoesNotExist:
                pass

            try:
                event = Event.objects.get(pk=obj.community.id)
                event.is_approved = True
                event.save()
            except Event.DoesNotExist:
                pass

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_membership_default_label(request):
    return Response({
        'club': {
            '3': _('President'),
            '2': _('Vice President'),
            '1': _('Staff'),
            '0': _('Member'),
        },
        'event': {
            '3': _('President'),
            '2': _('Vice President'),
            '1': _('Staff'),
            '0': _('Participator'),
        },
        'community_event': {
            '3': _('Event Creator'),
            '2': _('Event Co-Creator'),
            '1': _('Staff'),
            '0': _('Participator'),
        },
        'lab': {
            '3': _('Lab Supervisor'),
            '2': _('Lab Co-Supervisor'),
            '1': _('Lab Helper'),
            '0': _('Lab Member'),
        }
    })
