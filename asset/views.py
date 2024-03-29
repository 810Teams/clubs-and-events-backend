'''
    Asset Application Views
    asset/views.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.http import Http404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response

from asset.models import Announcement, Album, AlbumImage, Comment
from asset.permissions import IsAbleToRetrieveAnnouncement, IsAbleToDeleteComment, IsAbleToRetrieveAlbum
from asset.permissions import IsAbleToRetrieveAlbumImage
from asset.serializers import ExistingAnnouncementSerializer, NotExistingAnnouncementSerializer
from asset.serializers import ExistingAlbumSerializer, NotExistingAlbumSerializer
from asset.serializers import AlbumImageSerializer, CommentSerializer
from core.permissions import IsStaffOfCommunity, IsInPubliclyVisibleCommunity, IsInActiveCommunity
from core.utils.filters import filter_queryset, filter_queryset_permission, limit_queryset
from membership.models import Membership
from notification.notifier import notify


class AnnouncementViewSet(viewsets.ModelViewSet):
    ''' Announcement view set '''
    queryset = Announcement.objects.filter(is_active=True)
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('text',)

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (IsInActiveCommunity(), IsAbleToRetrieveAnnouncement())
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsStaffOfCommunity())
        return tuple()

    def get_serializer_class(self):
        ''' Get serializer class '''
        if self.request.method == 'POST':
            return NotExistingAnnouncementSerializer
        return ExistingAnnouncementSerializer

    def list(self, request, *args, **kwargs):
        ''' List announcements '''
        queryset = self.filter_queryset(self.get_queryset())

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='is_publicly_visible', is_foreign_key=False)
        queryset = limit_queryset(queryset, request)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        ''' Create announcement '''
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # Notification
        users = [
            i.user for i in Membership.objects.filter(community_id=obj.community.id, status='A').exclude(
                user_id=request.user.id
            )
        ]
        notify(users=users, obj=obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        ''' Disable instance '''
        announcement = self.get_object()
        announcement.is_active = False
        announcement.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AlbumViewSet(viewsets.ModelViewSet):
    ''' Album view set '''
    queryset = Album.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (IsInActiveCommunity(), IsAbleToRetrieveAlbum())
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsStaffOfCommunity())
        return tuple()

    def get_serializer_class(self):
        ''' Get serializer class '''
        if self.request.method == 'POST':
            return NotExistingAlbumSerializer
        return ExistingAlbumSerializer

    def list(self, request, *args, **kwargs):
        ''' List albums '''
        queryset = self.filter_queryset(self.get_queryset())

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='is_publicly_visible', is_foreign_key=False)
        queryset = filter_queryset(queryset, request, target_param='community', is_foreign_key=True)
        queryset = filter_queryset(queryset, request, target_param='community_event', is_foreign_key=True)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class AlbumImageViewSet(viewsets.ModelViewSet):
    ''' Album image view set '''
    queryset = AlbumImage.objects.all()
    serializer_class = AlbumImageSerializer
    http_method_names = ('get', 'post', 'delete', 'head', 'options')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (IsInActiveCommunity(), IsAbleToRetrieveAlbumImage())
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method == 'DELETE':
            return (permissions.IsAuthenticated(), IsInActiveCommunity(), IsStaffOfCommunity())
        return tuple()

    def list(self, request, *args, **kwargs):
        ''' List album images '''
        queryset = self.get_queryset()

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='album', is_foreign_key=True)
        queryset = limit_queryset(queryset, request)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        ''' Create album image '''
        serializer = self.get_serializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)

        # Update album's updater
        album = Album.objects.get(pk=request.data['album'])
        album.updated_by = request.user
        album.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        ''' Destroy album image '''
        try:
            instance = self.get_object()
            album_id = instance.album.id
            self.perform_destroy(instance)

            # Update album's updater
            album = Album.objects.get(pk=album_id)
            album.updated_by = request.user
            album.save()
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    ''' Comment view set '''
    queryset = Comment.objects.filter(is_active=True)
    serializer_class = CommentSerializer
    http_method_names = ('get', 'post', 'delete', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('text', 'written_by')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method == 'GET':
            return (IsInActiveCommunity(), IsInPubliclyVisibleCommunity())
        elif self.request.method == 'DELETE':
            return (IsInActiveCommunity(), IsAbleToDeleteComment(),)
        return tuple()

    def list(self, request, *args, **kwargs):
        ''' List comments '''
        queryset = self.filter_queryset(self.get_queryset())

        queryset = filter_queryset_permission(queryset, request, self.get_permissions())
        queryset = filter_queryset(queryset, request, target_param='event', is_foreign_key=True)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        ''' Disable instance '''
        comment = self.get_object()
        comment.is_active = False
        comment.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
