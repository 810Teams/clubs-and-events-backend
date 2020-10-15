from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.permissions import IsMemberOfCommunity, IsDeputyLeaderOfCommunity
from core.utils import filter_queryset
from generator.models import QRCode, JoinKey
from generator.serializers import ExistingQRCodeSerializer, NotExistingQRCodeSerializer
from generator.serializers import ExistingJoinKeySerializer, NotExistingJoinKeySerializer
from membership.models import Membership

import random


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
def generate_join_key(request):
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

    query = request.query_params.get('length')
    if query is not None:
        length = int(query)

        if length < 8 or length > 64:
            return Response({
                 'details': 'The length of the join key must be at least 8 characters but not more than 64 characters.'
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        length = 32

    while True:
        join_key = ''.join(random.choice(letters) for _ in range(length))
        try:
            JoinKey.objects.get(key=join_key)
        except JoinKey.DoesNotExist:
            return Response({'key': join_key}, status=status.HTTP_200_OK)


@api_view(['POST'])
def use_join_key(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        key = request.data['key']
    except KeyError:
        return Response({'detail': 'Join key was not provided.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        join_key = JoinKey.objects.get(key=key)

        try:
            membership = Membership.objects.get(user_id=request.user.id, community_id=join_key.event.id)

            if membership.status == 'A':
                return Response({'detail': 'Already a member.'}, status=status.HTTP_400_BAD_REQUEST)

            membership.position = 0
            membership.status = 'A'
            membership.save()

            return Response({'detail': 'Joined successful.'}, status=status.HTTP_200_OK)
        except Membership.DoesNotExist:
            Membership.objects.create(user_id=request.user.id, community_id=join_key.event.id)
            return Response({'detail': 'Joined successful.'}, status=status.HTTP_200_OK)

    except JoinKey.DoesNotExist:
        return Response({'detail': 'Invalid join key.'}, status=status.HTTP_404_NOT_FOUND)
