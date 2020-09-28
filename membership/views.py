from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from community.models import CommunityEvent
from core.permissions import IsStaffOfCommunity
from core.utils import filter_queryset
from membership.models import Request, Membership, Invitation, CustomMembershipLabel
from membership.permissions import IsRequestOwner, IsEditableRequest, IsCancellableRequest, IsAbleToViewRequestList
from membership.permissions import IsInvitationInvitee, IsInvitationInvitor, IsAbleToViewInvitationList
from membership.permissions import IsAbleToUpdateMembership
from membership.serializers import ExistingRequestSerializer, NotExistingRequestSerializer, MembershipSerializer
from membership.serializers import ExistingInvitationSerializer, NotExistingInvitationSerializer


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (permissions.IsAuthenticated(), IsAbleToViewRequestList())
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsStaffOfCommunity(), IsEditableRequest())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsRequestOwner(), IsCancellableRequest())
        return tuple()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotExistingRequestSerializer
        return ExistingRequestSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        memberships = Membership.objects.filter(user_id=request.user.id, status='A')
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
        obj = serializer.save(user=request.user, updated_by=request.user)

        community_event = CommunityEvent.objects.filter(pk=obj.community.id)
        if len(community_event) == 1:
            request_obj = Request.objects.get(pk=obj.id)
            request_obj.status = 'A'
            request_obj.save()
            Membership.objects.create(user_id=obj.user.id, position=0, community_id=obj.community.id,
                                      created_by_id=request.user.id, updated_by_id=request.user.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(updated_by=request.user)

        if obj.status == 'A':
            Membership.objects.create(user_id=obj.user.id, position=0, community_id=obj.community.id,
                                      created_by_id=request.user.id, updated_by_id=request.user.id)
        elif obj.status == 'W':
            return Response(
                {'error': 'Request statuses are not able to be updated to waiting.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.data, status=status.HTTP_200_OK)


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (permissions.IsAuthenticated(), IsAbleToViewInvitationList())
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),) # Includes IsStaffOfCommunity() in validation() of the serializer
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsInvitationInvitee())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsInvitationInvitor())
        return tuple()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotExistingInvitationSerializer
        return ExistingInvitationSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        memberships = Membership.objects.filter(user_id=request.user.id, status='A')
        communities = [i.community.id for i in memberships]

        id_set = [i.id for i in queryset.filter(community_id__in=communities)]
        id_set += [i.id for i in queryset.filter(invitor_id=request.user.id)]
        id_set += [i.id for i in queryset.filter(invitee_id=request.user.id)]

        queryset = queryset.filter(pk__in=id_set)

        queryset = filter_queryset(queryset, request, target_param='invitor', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='invitee', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(invitor=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        if obj.status == 'A':
            Membership.objects.create(user_id=obj.user.id, position=0, community_id=obj.community.id,
                                      created_by_id=request.user.id, updated_by_id=request.user.id)
        elif obj.status == 'W':
            return Response(
                {'error': 'Invitation statuses are not able to be updated to waiting.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.data, status=status.HTTP_200_OK)


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    http_method_names = ('get', 'put', 'patch', 'head', 'options')

    # TODO: Completes MembershipViewSet for changing position and removing members

    def get_permissions(self):
        if self.request.method == 'GET':
            return tuple()
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsAbleToUpdateMembership())
        return tuple()

    def update(self, request, *args, **kwargs):
        old_position = Membership.objects.get(pk=kwargs['pk']).position

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
            membership.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomMembershipLabelViewSet(viewsets.ModelViewSet):
    queryset = CustomMembershipLabel.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    # TODO: Completes CustomMembershipLabelViewSet for retrieving, adding, editing, and deleting labels
