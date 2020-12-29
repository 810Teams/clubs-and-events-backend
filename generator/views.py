'''
    Generator Application Views
    generator/views
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.permissions import IsMemberOfCommunity, IsDeputyLeaderOfCommunity, IsLeaderOfCommunity
from core.utils.filters import filter_queryset, filter_queryset_permission
from core.utils.general import get_random_string
from generator.models import QRCode, JoinKey, GeneratedDocx
from generator.serializers import ExistingQRCodeSerializer, NotExistingQRCodeSerializer
from generator.serializers import ExistingJoinKeySerializer, NotExistingJoinKeySerializer
from generator.serializers import ExistingGeneratedDocxSerializer, NotExistingGeneratedDocxSerializer
from membership.models import Membership

import random


class QRCodeViewSet(viewsets.ModelViewSet):
    ''' QR code view set '''
    queryset = QRCode.objects.all()
    http_method_names = ('get', 'post', 'delete', 'head', 'options')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (permissions.IsAuthenticated(), IsMemberOfCommunity())
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsDeputyLeaderOfCommunity())
        return tuple()

    def get_serializer_class(self):
        ''' Get serializer class '''
        if self.request.method == 'POST':
            return NotExistingQRCodeSerializer
        return ExistingQRCodeSerializer

    def list(self, request, *args, **kwargs):
        ''' List QR codes '''
        queryset = self.get_queryset()

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='event', is_foreign_key=True)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class JoinKeyViewSet(viewsets.ModelViewSet):
    ''' Join key view set '''
    queryset = JoinKey.objects.all()
    http_method_names = ('get', 'post', 'delete', 'head', 'options')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (permissions.IsAuthenticated(), IsMemberOfCommunity())
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsDeputyLeaderOfCommunity())
        return tuple()

    def get_serializer_class(self):
        ''' Get serializer class '''
        if self.request.method == 'POST':
            return NotExistingJoinKeySerializer
        return ExistingJoinKeySerializer

    def list(self, request, *args, **kwargs):
        ''' List join keys '''
        queryset = self.get_queryset()

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='event', is_foreign_key=True)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


@api_view(['GET'])
def generate_join_key(request):
    ''' Generate join key API '''
    # Validate join key's length
    query = request.query_params.get('length')
    if query is not None:
        try:
            length = int(query)
            if length < 8 or length > 64:
                return Response({
                    'details': 'The length of the join key must be an integer from 8 to 64.'
                }, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({
                'details': 'The length of the join key must be an integer from 8 to 64.'
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        length = 32

    # Generate join key, if duplicated, generate a new one
    while True:
        join_key = get_random_string(length=length)
        try:
            JoinKey.objects.get(key=join_key)
        except JoinKey.DoesNotExist:
            return Response({'key': join_key}, status=status.HTTP_200_OK)


@api_view(['POST'])
def use_join_key(request):
    ''' Use join key API '''
    # Check authentication
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_403_FORBIDDEN)

    # Check join key from POST request data
    try:
        key = request.data['key']
    except KeyError:
        return Response({'detail': 'Join key was not provided.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate join key
    try:
        join_key = JoinKey.objects.get(key=key)

        try:
            membership = Membership.objects.get(user_id=request.user.id, community_id=join_key.event.id)

            if IsMemberOfCommunity().has_object_permission(request, None, membership):
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


class GeneratedDocxViewSet(viewsets.ModelViewSet):
    ''' Generated Microsoft Word document view set '''
    queryset = GeneratedDocx.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method in ('GET', 'PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsDeputyLeaderOfCommunity())
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsDeputyLeaderOfCommunity())
        return tuple()

    def get_serializer_class(self):
        ''' Get serializer class '''
        if self.request.method == 'POST':
            return NotExistingGeneratedDocxSerializer
        return ExistingGeneratedDocxSerializer

    def list(self, request, *args, **kwargs):
        ''' List generated Microsoft Word documents '''
        queryset = self.get_queryset()

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='club', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='advisor', is_foreign_key=True)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)
