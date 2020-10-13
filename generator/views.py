from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.permissions import IsMemberOfCommunity, IsDeputyLeaderOfCommunity
from core.utils import filter_queryset
from generator.models import QRCode, JoinKey
from generator.serializers import ExistingQRCodeSerializer, NotExistingQRCodeSerializer
from generator.serializers import ExistingJoinKeySerializer, NotExistingJoinKeySerializer
from membership.models import Membership


class QRCodeViewSet(viewsets.ModelViewSet):
    queryset = QRCode.objects.all()
    http_method_names = ('get', 'post', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (permissions.IsAuthenticated(), IsMemberOfCommunity())
        elif self.request.method == 'POST':
            # Includes IsDeputyLeaderOfCommunity() in validate() of the serializer
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsDeputyLeaderOfCommunity())
        return tuple()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotExistingQRCodeSerializer
        return ExistingQRCodeSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        visible_ids = [i.community.id for i in Membership.objects.filter(user_id=request.user.id, status='A')]
        queryset = queryset.filter(community_id__in=visible_ids)

        queryset = filter_queryset(queryset, request, target_param='event', is_foreign_key=True)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class JoinKeyViewSet(viewsets.ModelViewSet):
    queryset = JoinKey.objects.all()
    http_method_names = ('get', 'post', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (permissions.IsAuthenticated(), IsMemberOfCommunity())
        elif self.request.method == 'POST':
            # Includes IsDeputyLeaderOfCommunity() in validate() of the serializer
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsDeputyLeaderOfCommunity())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsDeputyLeaderOfCommunity())
        return tuple()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotExistingJoinKeySerializer
        return ExistingJoinKeySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        visible_ids = [i.community.id for i in Membership.objects.filter(user_id=request.user.id, status='A')]
        queryset = queryset.filter(event_id__in=visible_ids)

        queryset = filter_queryset(queryset, request, target_param='event', is_foreign_key=True)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


@api_view(['GET'])
def use_join_key(request, key):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        join_key = JoinKey.objects.get(key=key)

        try:
            membership = Membership.objects.get(user_id=request.user.id, community_id=join_key.event.id)

            if membership.status == 'A':
                return Response({'detail': 'Already a member.'}, status=status.HTTP_400_BAD_REQUEST)

            membership.position = 0
            membership.status = 'A'
            membership.save()

            return Response({'detail': 'Join successful.'}, status=status.HTTP_200_OK)
        except Membership.DoesNotExist:
            Membership.objects.create(user_id=request.user.id, community_id=join_key.event.id)
            return Response({'detail': 'Join successful.'}, status=status.HTTP_200_OK)

    except JoinKey.DoesNotExist:
        return Response({'detail': 'Invalid join key.'}, status=status.HTTP_404_NOT_FOUND)
