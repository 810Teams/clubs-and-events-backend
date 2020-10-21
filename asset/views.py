from django.http import Http404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response

from asset.models import Announcement, Album, AlbumImage, Comment
from asset.serializers import ExistingAnnouncementSerializer, NotExistingAnnouncementSerializer
from asset.serializers import ExistingAlbumSerializer, NotExistingAlbumSerializer
from asset.serializers import AlbumImageSerializer, CommentSerializer
from community.models import Community
from core.permissions import IsStaffOfCommunity, IsInPubliclyVisibleCommunity
from core.utils import filter_queryset, limit_queryset, filter_queryset_permission, get_client_ip
from membership.models import Membership
from notification.notifier import notify


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('text',)

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsInPubliclyVisibleCommunity(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return (permissions.IsAuthenticated(), IsStaffOfCommunity())
        return tuple()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotExistingAnnouncementSerializer
        return ExistingAnnouncementSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # Notification
        users = [i.user for i in Membership.objects.filter(
            community_id=obj.community.id, status='A'
        )]
        notify(users=users, obj=obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsInPubliclyVisibleCommunity(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return (permissions.IsAuthenticated(), IsStaffOfCommunity())
        return tuple()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotExistingAlbumSerializer
        return ExistingAlbumSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class AlbumImageViewSet(viewsets.ModelViewSet):
    queryset = AlbumImage.objects.all()
    serializer_class = AlbumImageSerializer
    http_method_names = ('get', 'post', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsInPubliclyVisibleCommunity(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsStaffOfCommunity())
        return tuple()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not self.request.user.is_authenticated:
            visible_ids = Community.objects.filter(is_publicly_visible=True)
            queryset = queryset.filter(community_id__in=visible_ids)

        queryset = filter_queryset(queryset, request, target_param='album', is_foreign_key=True)
        queryset = limit_queryset(queryset, request)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)

        album = Album.objects.get(pk=request.data['album'])
        album.updated_by = request.user
        album.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            album_id = instance.album.id
            self.perform_destroy(instance)

            album = Album.objects.get(pk=album_id)
            album.updated_by = request.user
            album.save()
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ('get', 'post', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('text', 'written_by')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsInPubliclyVisibleCommunity(),)
        return tuple()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='event', is_foreign_key=True)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)
