from datetime import datetime

from rest_framework import status, permissions, viewsets
from rest_framework.response import Response

from community.models import Club, Event, CommunityEvent, Lab
from community.permissions import IsPubliclyVisible, IsLeaderOfCommunity, IsDeputyLeaderOfCommunity, IsDeletableClub, \
    IsDeletableLab, IsDeletableEvent, IsDeletableCommunityEvent, IsLeaderOfBaseCommunity, IsStaffOfBaseCommunity, \
    IsDeputyLeaderOfBaseCommunity
from community.serializers import LabSerializer, UnofficialClubSerializer, OfficialClubSerializer, \
    UnapprovedEventSerializer, ApprovedEventSerializer, NotExistingCommunityEventSerializer, \
    ExistingCommunityEventSerializer
from user.permissions import IsStudent, IsLecturer
from membership.models import Membership


class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsPubliclyVisible(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(), IsStudent())
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsStudent(), IsDeputyLeaderOfCommunity())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsStudent(), IsLeaderOfCommunity(), IsDeletableClub())
        return tuple()

    def get_serializer_class(self):
        try:
            if self.request.method == 'POST' or not self.get_object().is_official:
                return UnofficialClubSerializer
        except AssertionError:
            pass
        return OfficialClubSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not request.user.is_authenticated:
            queryset = queryset.filter(is_publicly_visible=True, is_official=True)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        serializer = self.get_serializer(data=data, many=False)

        if serializer.is_valid():
            obj = serializer.save()
            Membership.objects.create(user=user, position=3, community=obj, start_date=str(datetime.now().date()))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsPubliclyVisible(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(), IsStudent())
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsStudent(), IsDeputyLeaderOfCommunity())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsStudent(), IsLeaderOfCommunity(), IsDeletableEvent())
        return tuple()

    def get_serializer_class(self):
        try:
            if self.request.method == 'POST' or not self.get_object().is_approved:
                return UnapprovedEventSerializer
        except AssertionError:
            pass
        return ApprovedEventSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not request.user.is_authenticated:
            queryset = queryset.filter(is_publicly_visible=True, is_approved=True)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        serializer = self.get_serializer(data=data, many=False)

        if serializer.is_valid():
            obj = serializer.save()
            Membership.objects.create(user=user, position=3, community=obj, start_date=str(datetime.now().date()))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CommunityEventViewSet(viewsets.ModelViewSet):
    queryset = CommunityEvent.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsPubliclyVisible(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(), IsStaffOfBaseCommunity())
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsDeputyLeaderOfCommunity(), IsDeputyLeaderOfBaseCommunity())
        elif self.request.method == 'DELETE':
            return (
                permissions.IsAuthenticated(),
                IsLeaderOfCommunity() or IsLeaderOfBaseCommunity(),
                IsDeletableCommunityEvent()
            )
        return tuple()

    def get_serializer_class(self):
        try:
            if self.request.method == 'POST' or self.get_object() is None:
                return NotExistingCommunityEventSerializer
        except AssertionError:
            pass
        return ExistingCommunityEventSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not request.user.is_authenticated:
            queryset = queryset.filter(is_publicly_visible=True)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        serializer = self.get_serializer(data=data, many=False)

        if serializer.is_valid():
            obj = serializer.save()
            Membership.objects.create(user=user, position=3, community=obj, start_date=str(datetime.now().date()))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LabViewSet(viewsets.ModelViewSet):
    queryset = Lab.objects.all()
    serializer_class = LabSerializer
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsPubliclyVisible(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(), IsLecturer())
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsLecturer(), IsDeputyLeaderOfCommunity())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsLecturer(), IsLeaderOfCommunity(), IsDeletableLab())
        return tuple()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not request.user.is_authenticated:
            queryset = queryset.filter(is_publicly_visible=True)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        serializer = self.get_serializer(data=data, many=False)

        if serializer.is_valid():
            obj = serializer.save()
            Membership.objects.create(user=user, position=3, community=obj, start_date=str(datetime.now().date()))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
