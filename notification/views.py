'''
    Notification Application Views
    notification/views.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import permissions, viewsets
from rest_framework.response import Response

from core.utils.filters import filter_queryset_permission
from notification.models import Notification, RequestNotification, MembershipLogNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification
from notification.permissions import IsNotificationOwner
from notification.serializers import NotificationSerializer, RequestNotificationSerializer
from notification.serializers import MembershipLogNotificationSerializer, AnnouncementNotificationSerializer
from notification.serializers import CommunityEventNotificationSerializer, EventNotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    ''' Notification view set '''
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated, IsNotificationOwner)
    http_method_names = ('get', 'put', 'patch', 'delete', 'head', 'options')

    def list(self, request, *args, **kwargs):
        ''' List notifications '''
        queryset = self.get_queryset()
        queryset = filter_queryset_permission(queryset, request, self.get_permissions())

        try:
            limit = request.query_params.get('limit')
            if limit is not None:
                queryset = queryset[len(queryset) - 1 - int(limit):len(queryset)]
        except ValueError:
            queryset = None

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class RequestNotificationViewSet(NotificationViewSet):
    ''' Request notification view set '''
    queryset = RequestNotification.objects.all()
    serializer_class = RequestNotificationSerializer


class MembershipLogNotificationViewSet(NotificationViewSet):
    ''' Membership log notification view set '''
    queryset = MembershipLogNotification.objects.all()
    serializer_class = MembershipLogNotificationSerializer


class AnnouncementNotificationViewSet(NotificationViewSet):
    ''' Announcement notification view set '''
    queryset = AnnouncementNotification.objects.all()
    serializer_class = AnnouncementNotificationSerializer


class CommunityEventNotificationViewSet(NotificationViewSet):
    ''' Community event notification view set '''
    queryset = CommunityEventNotification.objects.all()
    serializer_class = CommunityEventNotificationSerializer


class EventNotificationViewSet(NotificationViewSet):
    ''' Event notification view set '''
    queryset = EventNotification.objects.all()
    serializer_class = EventNotificationSerializer
