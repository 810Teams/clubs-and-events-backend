from rest_framework import permissions, viewsets

from notification.models import Notification, RequestNotification, MembershipLogNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification
from notification.permissions import IsNotificationOwner
from notification.serializers import NotificationSerializer, RequestNotificationSerializer
from notification.serializers import MembershipLogNotificationSerializer, AnnouncementNotificationSerializer
from notification.serializers import CommunityEventNotificationSerializer, EventNotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated, IsNotificationOwner)
    http_method_names = ('get', 'put', 'patch', 'delete', 'head', 'options')


class RequestNotificationViewSet(NotificationViewSet):
    queryset = RequestNotification.objects.all()
    serializer_class = RequestNotificationSerializer


class MembershipLogNotificationViewSet(NotificationViewSet):
    queryset = MembershipLogNotification.objects.all()
    serializer_class = MembershipLogNotificationSerializer


class AnnouncementNotificationViewSet(NotificationViewSet):
    queryset = AnnouncementNotification.objects.all()
    serializer_class = AnnouncementNotificationSerializer


class CommunityEventNotificationViewSet(NotificationViewSet):
    queryset = CommunityEventNotification.objects.all()
    serializer_class = CommunityEventNotificationSerializer


class EventNotificationViewSet(NotificationViewSet):
    queryset = EventNotification.objects.all()
    serializer_class = EventNotificationSerializer
