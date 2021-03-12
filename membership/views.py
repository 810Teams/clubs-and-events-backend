'''
    Membership Application Views
    membership/views.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from clubs_and_events.settings import CLUB_VALID_MONTH, CLUB_VALID_DAY, CLUB_ADVANCED_RENEWAL
from community.models import Club, Event, CommunityEvent, Lab, Community
from community.permissions import IsRenewableClub, IsMemberOfBaseCommunity
from core.permissions import IsInPubliclyVisibleCommunity, IsInActiveCommunity, IsDeputyLeaderOfCommunity
from core.utils.filters import filter_queryset, filter_queryset_permission, get_latest_membership_log
from core.utils.filters import get_active_community_ids
from core.utils.general import has_instance, remove_duplicates
from membership.models import Request, Membership, Invitation, CustomMembershipLabel, Advisory, MembershipLog
from membership.models import ApprovalRequest
from membership.permissions import IsAbleToRetrieveRequest, IsAbleToUpdateRequest, IsAbleToDeleteRequest
from membership.permissions import IsAbleToRetrieveInvitation, IsAbleToUpdateInvitation, IsAbleToDeleteInvitation
from membership.permissions import IsAbleToUpdateMembership, IsAbleToUpdateCustomMembershipLabel
from membership.permissions import IsAbleToRetrieveApprovalRequest, IsAbleToUpdateApprovalRequest
from membership.permissions import IsAbleToDeleteApprovalRequest, IsAbleToCreateAndDeleteAdvisory
from membership.serializers import ExistingRequestSerializer, NotExistingRequestSerializer
from membership.serializers import ExistingInvitationSerializer, NotExistingInvitationSerializer
from membership.serializers import MembershipSerializer, MembershipLogSerializer, AdvisorySerializer
from membership.serializers import NotExistingCustomMembershipLabelSerializer, ExistingCustomMembershipLabelSerializer
from membership.serializers import ExistingApprovalRequestSerializer, NotExistingApprovalRequestSerializer
from notification.notifier import notify, notify_membership_log


class RequestViewSet(viewsets.ModelViewSet):
    ''' Request view set '''
    queryset = Request.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsAbleToRetrieveRequest())
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsAbleToUpdateRequest())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsAbleToDeleteRequest())
        return tuple()

    def get_serializer_class(self):
        ''' Get serializer class '''
        if self.request.method == 'POST':
            return NotExistingRequestSerializer
        return ExistingRequestSerializer

    def list(self, request, *args, **kwargs):
        ''' List requests '''
        queryset = self.get_queryset()

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='user', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        ''' Create request '''
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # Requesting to join the community event
        # If already a member of base community, you can join without waiting to be approved.
        instant_join = False
        if has_instance(obj.community, CommunityEvent):
            community_event = CommunityEvent.objects.get(pk=obj.community.id)
            if IsMemberOfBaseCommunity().has_object_permission(request, None, community_event):
                # Check for past membership to renew it, otherwise, create a new one.
                try:
                    membership = Membership.objects.get(user_id=obj.user.id, community_id=obj.community.id)
                    membership.position = 0
                    membership.status = 'A'
                    membership.save()
                except Membership.DoesNotExist:
                    membership = Membership.objects.create(user_id=obj.user.id, community_id=obj.community.id)

                # Update request status
                obj.status = 'A'
                obj.save()

                # Skip request notification, use membership log notification instead
                instant_join = True
                notify_membership_log(get_latest_membership_log(membership))

        # Notification
        if not instant_join:
            users = [i.user for i in Membership.objects.filter(
                community_id=obj.community.id, position__in=(1, 2, 3), status='A'
            )]
            notify(users=users, obj=obj)

        serializer = self.get_serializer(obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        ''' Update request '''
        serializer = self.get_serializer(self.get_object(), data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # If the request is accepted, check for past membership to renew it, otherwise, create a new one.
        if obj.status == 'A':
            try:
                membership = Membership.objects.get(user_id=obj.user.id, community_id=obj.community.id)
                membership.position = 0
                membership.status = 'A'
                membership.save()
            except Membership.DoesNotExist:
                membership = Membership.objects.create(user_id=obj.user.id, community_id=obj.community.id)

            # Request accepted notification
            notify(users=(obj.user,), obj=obj)

            # New member joined notification
            notify_membership_log(get_latest_membership_log(membership))

        return Response(serializer.data, status=status.HTTP_200_OK)


class InvitationViewSet(viewsets.ModelViewSet):
    ''' Invitation view set '''
    queryset = Invitation.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsAbleToRetrieveInvitation())
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsAbleToUpdateInvitation())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsAbleToDeleteInvitation())
        return tuple()

    def get_serializer_class(self):
        ''' Get serializer class '''
        if self.request.method == 'POST':
            return NotExistingInvitationSerializer
        return ExistingInvitationSerializer

    def list(self, request, *args, **kwargs):
        ''' List invitations '''
        queryset = self.get_queryset()

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='invitor', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='invitee', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        ''' Create invitation '''
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        notify((obj.invitee,), obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        ''' Update invitation '''
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
                membership = Membership.objects.create(user_id=obj.invitee.id, community_id=obj.community.id)

            # Notification
            notify_membership_log(get_latest_membership_log(membership))

        return Response(serializer.data, status=status.HTTP_200_OK)


class MembershipViewSet(viewsets.ModelViewSet):
    ''' Membership view set '''
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    http_method_names = ('get', 'put', 'patch', 'head', 'options')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (IsInActiveCommunity(), IsInPubliclyVisibleCommunity())
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsAbleToUpdateMembership())
        return tuple()

    def list(self, request, *args, **kwargs):
        ''' List memberships '''
        queryset = self.get_queryset()

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='user', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='position', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)

        # Community Type Filtering
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

        # Custom Searching
        try:
            query = request.query_params.get('search')
            if query is not None:
                filtered_ids = [i.id for i in queryset if query in i.user.name]
                queryset = queryset.filter(pk__in=filtered_ids)
        except ValueError:
            queryset = None

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        ''' Update membership '''
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

        # Notification
        notify_membership_log(get_latest_membership_log(obj))

        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomMembershipLabelViewSet(viewsets.ModelViewSet):
    ''' Custom membership label view set '''
    queryset = CustomMembershipLabel.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (IsInActiveCommunity(), IsInPubliclyVisibleCommunity())
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsAbleToUpdateCustomMembershipLabel())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsDeputyLeaderOfCommunity())
        return tuple()

    def get_serializer_class(self):
        ''' Get serializer class '''
        if self.request.method == 'POST':
            return NotExistingCustomMembershipLabelSerializer
        return ExistingCustomMembershipLabelSerializer

    def list(self, request, *args, **kwargs):
        ''' List custom membership labels '''
        queryset = self.get_queryset()
        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class MembershipLogViewSet(viewsets.ModelViewSet):
    ''' Membership log view set '''
    queryset = MembershipLog.objects.all()
    serializer_class = MembershipLogSerializer
    http_method_names = ('get', 'head', 'options')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (IsInActiveCommunity(), IsInPubliclyVisibleCommunity())
        return tuple()

    def list(self, request, *args, **kwargs):
        ''' List membership logs '''
        queryset = self.get_queryset()

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())

        try:
            # Filter selected user
            query = request.query_params.get('user')
            if query is not None:
                membership_ids = [i.id for i in Membership.objects.filter(user_id=query)]
                queryset = queryset.filter(membership_id__in=membership_ids)

            # Filter selected community
            query = request.query_params.get('community')
            if query is not None:
                membership_ids = [i.id for i in Membership.objects.filter(community_id=query)]
                queryset = queryset.filter(membership_id__in=membership_ids)

            # Filter out current memberships
            query = request.query_params.get('exclude_current_memberships')
            if query is not None and eval(query):
                queryset = queryset.exclude(end_datetime=None)
        except ValueError:
            queryset = None

        queryset = filter_queryset(queryset, request, target_param='position', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class AdvisoryViewSet(viewsets.ModelViewSet):
    ''' Advisory view set '''
    queryset = Advisory.objects.all()
    serializer_class = AdvisorySerializer
    http_method_names = ('get', 'post', 'delete', 'head', 'options')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (IsInPubliclyVisibleCommunity(),)
        elif self.request.method in ('POST', 'DELETE'):
            return (permissions.IsAuthenticated(), IsAbleToCreateAndDeleteAdvisory())
        return tuple()

    def list(self, request, *args, **kwargs):
        ''' List advisories '''
        queryset = self.get_queryset()

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
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


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    ''' Approval request view set '''
    queryset = ApprovalRequest.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsAbleToRetrieveApprovalRequest())
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsAbleToUpdateApprovalRequest())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsAbleToDeleteApprovalRequest())
        return (permissions.IsAuthenticated(),)

    def get_serializer_class(self):
        ''' Get serializer class '''
        if self.request.method == 'POST':
            return NotExistingApprovalRequestSerializer
        return ExistingApprovalRequestSerializer

    def list(self, request, *args, **kwargs):
        ''' List approval requests '''
        queryset = self.get_queryset()

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        ''' Update approval request '''
        serializer = self.get_serializer(self.get_object(), data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        if obj.status == 'A':
            if has_instance(obj.community, Club):
                club = Club.objects.get(pk=obj.community.id)
                club.is_official = True

                today = datetime.now().date()

                if IsRenewableClub().has_object_permission(request, None, club):
                    valid_through = datetime(today.year, CLUB_VALID_MONTH, CLUB_VALID_DAY).date()

                    if today >= valid_through - CLUB_ADVANCED_RENEWAL:
                        valid_through = datetime(today.year + 1, CLUB_VALID_MONTH, CLUB_VALID_DAY).date()

                    club.valid_through = valid_through

                club.save()

            elif has_instance(obj.community, Event) and not has_instance(obj.community, CommunityEvent):
                event = Event.objects.get(pk=obj.community.id)
                event.is_approved = True
                event.save()

                # Notification
                if datetime.today().date() <= event.end_date:
                    notify(get_user_model().objects.all(), event)

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_membership_default_labels(request):
    ''' Get membership default labels API '''
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


@api_view(['GET'])
def get_past_memberships(request, user_id):
    ''' Get past memberships of a certain user API '''
    # Validate user
    try:
        get_user_model().objects.get(pk=user_id)
    except get_user_model().DoesNotExist:
        return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Filter past memberships of the user in active communities
    memberships = Membership.objects.filter(
        user_id=user_id, community_id__in=get_active_community_ids()
    ).exclude(status='A')

    # Exclude non-publicly visible communities if the current user is unauthenticated
    if not request.user.is_authenticated:
        memberships = memberships.exclude(is_publicly_visible=False)

    # Retrieve all past logs excluding the latest one
    membership_logs = MembershipLog.objects.filter(
        membership_id__in=[i.id for i in memberships]
    ).exclude(end_datetime=None)

    # Retrieve all related community IDs
    community_ids = remove_duplicates([i.membership.community.id for i in membership_logs])
    past_memberships = list()

    # Retrieve data according to each community ID
    for i in community_ids:
        # Retrieve community type
        _community = Community.objects.get(pk=i)
        if has_instance(_community, Club):
            _community_type = 'club'
        elif has_instance(_community, Event) and not has_instance(_community, CommunityEvent):
            _community_type = 'event'
        elif has_instance(_community, CommunityEvent):
            _community_type = 'community_event'
        elif has_instance(_community, Lab):
            _community_type = 'lab'
        else:
            _community_type = 'community'

        # Filter membership logs of a certain community
        _membership_logs = membership_logs.filter(membership_id__in=[j.id for j in memberships.filter(community_id=i)])

        # Retrieve position
        _position = max([j.position for j in _membership_logs])

        # Retrieve other data
        past_memberships.append({
            'community_id': i,
            'community_type': _community_type,
            'start_datetime': min([j.start_datetime for j in _membership_logs]),
            'end_datetime': max([j.end_datetime for j in _membership_logs]),
            'position': _position,
            'position_start_datetime': min([j.start_datetime for j in _membership_logs.filter(position=_position)]),
            'position_end_datetime': max([j.end_datetime for j in _membership_logs.filter(position=_position)])
        })

    return Response(past_memberships, status=status.HTTP_200_OK)
