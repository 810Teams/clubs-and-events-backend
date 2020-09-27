from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response

from community.models import Club, Event, CommunityEvent, Lab
from community.permissions import IsPubliclyVisibleCommunity
from community.permissions import IsLeaderOfBaseCommunity, IsDeputyLeaderOfBaseCommunity, IsStaffOfBaseCommunity
from community.permissions import IsDeletableClub, IsDeletableEvent, IsDeletableCommunityEvent, IsDeletableLab
from community.serializers import OfficialClubSerializer, UnofficialClubSerializer
from community.serializers import ApprovedEventSerializer, UnapprovedEventSerializer
from community.serializers import ExistingCommunityEventSerializer, NotExistingCommunityEventSerializer
from community.serializers import LabSerializer
from core.permissions import IsLeaderOfCommunity, IsDeputyLeaderOfCommunity
from core.utils import filter_queryset
from membership.models import Membership
from user.permissions import IsStudent, IsLecturer


class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name_th', 'name_en', 'description')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsPubliclyVisibleCommunity(),)
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

        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_publicly_visible=True, is_official=True)

        queryset = filter_queryset(queryset, request, target_param='club_type', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='is_official', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(created_by=request.user, updated_by=request.user)
        Membership.objects.create(user_id=request.user.id, position=3, community_id=obj.id,
                                  created_by_id=request.user.id, updated_by_id=request.user.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name_th', 'name_en', 'description', 'location')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsPubliclyVisibleCommunity(),)
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

        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_publicly_visible=True, is_approved=True)

        queryset = filter_queryset(queryset, request, target_param='event_type', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='event_series', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='is_approved', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='is_cancelled', is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(created_by=request.user, updated_by=request.user)
        Membership.objects.create(user_id=request.user.id, position=3, community_id=obj.id,
                                  created_by_id=request.user.id, updated_by_id=request.user.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CommunityEventViewSet(viewsets.ModelViewSet):
    queryset = CommunityEvent.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name_th', 'name_en', 'description', 'location')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsPubliclyVisibleCommunity(),)
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

        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_publicly_visible=True)

        queryset = filter_queryset(queryset, request, target_param='event_type', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='event_series', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='is_approved', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='is_cancelled', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='created_under', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='allows_outside_participators',
                                   is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(created_by=request.user, updated_by=request.user)
        Membership.objects.create(user_id=request.user.id, position=3, community_id=obj.id,
                                  created_by_id=request.user.id, updated_by_id=request.user.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LabViewSet(viewsets.ModelViewSet):
    queryset = Lab.objects.all()
    serializer_class = LabSerializer
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name_th', 'name_en', 'description', 'tags')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsPubliclyVisibleCommunity(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(), IsLecturer())
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsLecturer(), IsDeputyLeaderOfCommunity())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsLecturer(), IsLeaderOfCommunity(), IsDeletableLab())
        return tuple()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_publicly_visible=True)

        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(created_by=request.user, updated_by=request.user)
        Membership.objects.create(user_id=request.user.id, position=3, community_id=obj.id,
                                  created_by_id=request.user.id, updated_by_id=request.user.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)
