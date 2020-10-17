from django.contrib.auth import get_user_model
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response

from community.models import Club, Event, CommunityEvent, Lab
from community.permissions import IsPubliclyVisibleCommunity, IsAbleToUpdateClub, IsAbleToDeleteClub
from community.permissions import IsAbleToDeleteEvent, IsAbleToUpdateCommunityEvent, IsAbleToDeleteCommunityEvent
from community.permissions import IsAbleToUpdateLab, IsAbleToDeleteLab
from community.serializers import OfficialClubSerializer, UnofficialClubSerializer
from community.serializers import ApprovedEventSerializer, UnapprovedEventSerializer
from community.serializers import ExistingCommunityEventSerializer, NotExistingCommunityEventSerializer
from community.serializers import LabSerializer
from core.permissions import IsDeputyLeaderOfCommunity
from core.utils import filter_queryset, filter_queryset_permission
from membership.models import Membership
from notification.notifier import notify
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
            return (permissions.IsAuthenticated(), IsAbleToUpdateClub())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsAbleToDeleteClub())
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

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='club_type', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='is_official', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='url_id', is_foreign_key=False)

        if request.query_params.get('url_id') is not None and len(queryset) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif request.query_params.get('url_id') is not None and len(queryset) == 1:
            serializer = self.get_serializer(queryset[0], many=False)
        else:
            serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        Membership.objects.create(user_id=request.user.id, position=3, community_id=obj.id,)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name_th', 'name_en', 'description', 'location')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsPubliclyVisibleCommunity(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsDeputyLeaderOfCommunity())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsAbleToDeleteEvent())
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

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())

        try:
            query = request.query_params.get('exclude_community_events')
            if query is not None:
                if eval(query):
                    community_event_list = [i.id for i in CommunityEvent.objects.all()]
                    queryset = queryset.exclude(pk__in=community_event_list)
        except ValueError:
            queryset = None

        queryset = filter_queryset(queryset, request, target_param='event_type', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='event_series', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='is_approved', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='is_cancelled', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='url_id', is_foreign_key=False)

        if request.query_params.get('url_id') is not None and len(queryset) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif request.query_params.get('url_id') is not None and len(queryset) == 1:
            serializer = self.get_serializer(queryset[0], many=False)
        else:
            serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # Initial Membership
        Membership.objects.create(user_id=request.user.id, position=3, community_id=obj.id)

        # Notification
        users = get_user_model().objects.exclude(pk=request.user.id)
        notify(users=users, obj=obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommunityEventViewSet(viewsets.ModelViewSet):
    queryset = CommunityEvent.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name_th', 'name_en', 'description', 'location')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsPubliclyVisibleCommunity(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsAbleToUpdateCommunityEvent())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsAbleToDeleteCommunityEvent())
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

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='event_type', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='event_series', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='is_approved', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='is_cancelled', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='created_under', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='allows_outside_participators', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='url_id', is_foreign_key=False)

        if request.query_params.get('url_id') is not None and len(queryset) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif request.query_params.get('url_id') is not None and len(queryset) == 1:
            serializer = self.get_serializer(queryset[0], many=False)
        else:
            serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(is_approved=True)

        # Initial Membership
        Membership.objects.create(user_id=request.user.id, position=3, community_id=obj.id)

        # Notification
        users = [i.user for i in Membership.objects.filter(community_id=obj.created_under.id, status='A')]
        notify(users=users, obj=obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
            return (permissions.IsAuthenticated(), IsAbleToUpdateLab())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsAbleToDeleteLab())
        return tuple()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='url_id', is_foreign_key=False)

        if request.query_params.get('url_id') is not None and len(queryset) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif request.query_params.get('url_id') is not None and len(queryset) == 1:
            serializer = self.get_serializer(queryset[0], many=False)
        else:
            serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        Membership.objects.create(user_id=request.user.id, position=3, community_id=obj.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
