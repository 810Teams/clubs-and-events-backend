'''
    Community Application Views
    community/views.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from datetime import datetime

from rest_framework import filters, permissions, status, viewsets, generics
from rest_framework.response import Response

from community.models import Community, Club, Event, CommunityEvent, Lab
from community.permissions import IsPubliclyVisibleCommunity, IsAbleToUpdateClub, IsAbleToDeleteClub
from community.permissions import IsAbleToDeleteEvent, IsAbleToUpdateCommunityEvent, IsAbleToDeleteCommunityEvent
from community.permissions import IsAbleToUpdateLab, IsAbleToDeleteLab
from community.serializers import CommunitySerializer, OfficialClubSerializer, UnofficialClubSerializer
from community.serializers import ApprovedEventSerializer, UnapprovedEventSerializer
from community.serializers import ExistingCommunityEventSerializer, NotExistingCommunityEventSerializer
from community.serializers import LabSerializer
from core.permissions import IsDeputyLeaderOfCommunity, IsMemberOfCommunity, IsInActiveCommunity
from core.utils.filters import filter_queryset, filter_queryset_permission, filter_queryset_exclude_own, limit_queryset
from membership.models import Membership
from notification.notifier import notify
from user.permissions import IsStudent, IsLecturer


class CommunityViewSet(viewsets.ModelViewSet):
    ''' Community view set'''
    queryset = Community.objects.filter(is_active=True)
    permission_classes = (IsPubliclyVisibleCommunity,)
    serializer_class = CommunitySerializer
    http_method_names = ('get', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name_th', 'name_en', 'description')

    def list(self, request, *args, **kwargs):
        ''' List communities '''
        queryset = self.filter_queryset(self.get_queryset())

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='url_id', is_foreign_key=False)
        queryset = filter_queryset_exclude_own(queryset, request)
        queryset = limit_queryset(queryset, request)

        if request.query_params.get('url_id') is not None and len(queryset) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif request.query_params.get('url_id') is not None and len(queryset) == 1:
            serializer = self.get_serializer(queryset[0], many=False)
        else:
            serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        ''' Disable instance '''
        community = self.get_object()
        community.is_active = False
        community.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ClubViewSet(viewsets.ModelViewSet):
    ''' Club view set '''
    queryset = Club.objects.filter(is_active=True)
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name_th', 'name_en', 'description')

    def get_permissions(self):
        ''' Get permissions '''
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
        ''' Get serializer class '''
        try:
            if self.request.method == 'POST' or not self.get_object().is_official:
                return UnofficialClubSerializer
        except AssertionError:
            pass
        return OfficialClubSerializer

    def list(self, request, *args, **kwargs):
        ''' List clubs '''
        queryset = self.filter_queryset(self.get_queryset())

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='club_type', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='is_official', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='url_id', is_foreign_key=False)
        queryset = filter_queryset_exclude_own(queryset, request)
        queryset = limit_queryset(queryset, request)

        if request.query_params.get('url_id') is not None and len(queryset) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif request.query_params.get('url_id') is not None and len(queryset) == 1:
            serializer = self.get_serializer(queryset[0], many=False)
        else:
            serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        ''' Create club '''
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # Initial Membership
        Membership.objects.create(user_id=request.user.id, position=3, community_id=obj.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        ''' Disable instance '''
        community = self.get_object()
        community.is_active = False
        community.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class EventViewSet(viewsets.ModelViewSet):
    ''' Event view set '''
    queryset = Event.objects.filter(is_active=True)
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name_th', 'name_en', 'description', 'location')

    def get_permissions(self):
        ''' Get permissions '''
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
        ''' Get serializer class '''
        try:
            if self.request.method == 'POST' or not self.get_object().is_approved:
                return UnapprovedEventSerializer
        except AssertionError:
            pass
        return ApprovedEventSerializer

    def list(self, request, *args, **kwargs):
        ''' List events '''
        queryset = self.filter_queryset(self.get_queryset())

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='event_type', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='event_series', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='is_approved', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='is_cancelled', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='url_id', is_foreign_key=False)
        queryset = filter_queryset_exclude_own(queryset, request)
        queryset = limit_queryset(queryset, request)

        try:
            query = request.query_params.get('exclude_community_events')
            if query is not None and eval(query):
                community_event_list = [i.id for i in CommunityEvent.objects.all()]
                queryset = queryset.exclude(pk__in=community_event_list)
        except ValueError:
            queryset = None

        if request.query_params.get('url_id') is not None and len(queryset) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif request.query_params.get('url_id') is not None and len(queryset) == 1:
            serializer = self.get_serializer(queryset[0], many=False)
        else:
            serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        ''' Create event '''
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # Initial Membership
        Membership.objects.create(user_id=request.user.id, position=3, community_id=obj.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        ''' Disable instance '''
        community = self.get_object()
        community.is_active = False
        community.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CommunityEventViewSet(viewsets.ModelViewSet):
    ''' Community event view set '''
    queryset = CommunityEvent.objects.filter(is_active=True)
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name_th', 'name_en', 'description', 'location')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (IsInActiveCommunity(), IsPubliclyVisibleCommunity(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(), IsInActiveCommunity())
        elif self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsAbleToUpdateCommunityEvent())
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsAbleToDeleteCommunityEvent())
        return tuple()

    def get_serializer_class(self):
        ''' Get serializer class '''
        try:
            if self.request.method == 'POST' or self.get_object() is None:
                return NotExistingCommunityEventSerializer
        except AssertionError:
            pass
        return ExistingCommunityEventSerializer

    def list(self, request, *args, **kwargs):
        ''' List community events '''
        queryset = self.filter_queryset(self.get_queryset())

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='event_type', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='event_series', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='is_approved', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='is_cancelled', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='created_under', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='allows_outside_participators', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='url_id', is_foreign_key=False)
        queryset = filter_queryset_exclude_own(queryset, request)
        queryset = limit_queryset(queryset, request)

        if request.query_params.get('url_id') is not None and len(queryset) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif request.query_params.get('url_id') is not None and len(queryset) == 1:
            serializer = self.get_serializer(queryset[0], many=False)
        else:
            serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        ''' Create community event '''
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(is_approved=True)

        # Initial Membership
        Membership.objects.create(user_id=request.user.id, position=3, community_id=obj.id)

        # Notification
        if datetime.today().date() <= obj.end_date:
            users = [
                i.user for i in Membership.objects.filter(community_id=obj.created_under.id, status='A').exclude(
                    user_id=request.user.id
                )
            ]
            notify(users=users, obj=obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        ''' Disable instance '''
        community = self.get_object()
        community.is_active = False
        community.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class LabViewSet(viewsets.ModelViewSet):
    ''' Lab view set '''
    queryset = Lab.objects.filter(is_active=True)
    serializer_class = LabSerializer
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name_th', 'name_en', 'description', 'tags')

    def get_permissions(self):
        ''' Get permissions '''
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
        ''' List labs '''
        queryset = self.filter_queryset(self.get_queryset())

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='status', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='url_id', is_foreign_key=False)
        queryset = filter_queryset_exclude_own(queryset, request)
        queryset = limit_queryset(queryset, request)

        if request.query_params.get('url_id') is not None and len(queryset) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif request.query_params.get('url_id') is not None and len(queryset) == 1:
            serializer = self.get_serializer(queryset[0], many=False)
        else:
            serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        ''' Create lab '''
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # Initial Membership
        Membership.objects.create(user_id=request.user.id, position=3, community_id=obj.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        ''' Disable instance '''
        community = self.get_object()
        community.is_active = False
        community.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class MyCommunityView(generics.ListAPIView):
    ''' My community view '''
    queryset = Community.objects.filter(is_active=True)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CommunitySerializer

    def list(self, request, *args, **kwargs):
        ''' Retrieve own communities '''
        queryset = self.get_queryset().filter(
            id__in=[i.id for i in self.get_queryset() if IsMemberOfCommunity().has_object_permission(request, None, i)]
        )
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class MyClubView(MyCommunityView):
    ''' My club view '''
    queryset = Club.objects.filter(is_active=True)
    serializer_class = OfficialClubSerializer


class MyEventView(generics.ListAPIView):
    ''' My event view '''
    queryset = Event.objects.filter(is_active=True)
    serializer_class = ApprovedEventSerializer

    def list(self, request, *args, **kwargs):
        ''' Retrieve own events '''
        queryset = self.get_queryset().filter(
            id__in=[i.id for i in self.get_queryset() if IsMemberOfCommunity().has_object_permission(request, None, i)]
        )

        try:
            query = request.query_params.get('exclude_community_events')
            if query is not None and eval(query):
                community_event_list = [i.id for i in CommunityEvent.objects.all()]
                queryset = queryset.exclude(pk__in=community_event_list)
        except ValueError:
            queryset = None

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class MyCommunityEventView(MyCommunityView):
    ''' My community event view '''
    queryset = CommunityEvent.objects.filter(is_active=True)
    serializer_class = ExistingCommunityEventSerializer


class MyLabView(MyCommunityView):
    ''' My lab view '''
    queryset = Lab.objects.filter(is_active=True)
    serializer_class = LabSerializer
