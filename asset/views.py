from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from asset.models import Announcement
from asset.permissions import IsInPubliclyVisibleCommunity
from asset.serializers import ExistingAnnouncementSerializer, NotExistingAnnouncementSerializer
from community.models import Community
from community.permissions import IsStaffOfCommunity


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsInPubliclyVisibleCommunity(),)
        elif self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return (permissions.IsAuthenticated(), IsStaffOfCommunity())
        return tuple()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotExistingAnnouncementSerializer
        return ExistingAnnouncementSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not request.user.is_authenticated:
            visible_ids = Community.objects.filter(is_publicly_visible=True)
            queryset = queryset.filter(community_id__in=visible_ids)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        serializer = self.get_serializer(data=data, many=False)

        if serializer.is_valid():
            serializer.save(created_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
