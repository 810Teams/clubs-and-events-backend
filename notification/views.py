'''
    Notification Application Views
    notification/views.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import permissions, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from asset.models import Announcement
from community.models import Event, CommunityEvent
from core.permissions import IsInActiveCommunity
from core.utils.filters import filter_queryset_permission
from core.utils.users import get_email
from membership.models import Request, Invitation
from notification.models import Notification, RequestNotification, MembershipLogNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification
from notification.notifier import send_mail_notification
from notification.permissions import IsNotificationOwner
from notification.serializers import NotificationSerializer, RequestNotificationSerializer
from notification.serializers import MembershipLogNotificationSerializer, AnnouncementNotificationSerializer
from notification.serializers import CommunityEventNotificationSerializer, EventNotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    ''' Notification view set '''
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated, IsInActiveCommunity, IsNotificationOwner)
    http_method_names = ('get', 'put', 'patch', 'delete', 'head', 'options')

    def list(self, request, *args, **kwargs):
        ''' List notifications '''
        queryset = self.get_queryset()
        queryset = filter_queryset_permission(queryset, request, self.get_permissions())

        try:
            limit = request.query_params.get('limit')
            if limit is not None:
                queryset = queryset[max(len(queryset) - int(limit), 0):len(queryset)]
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


@api_view(['POST'])
def test_send_mail(request):
    ''' Test send mail API '''
    # Check superuser authentication
    if not request.user.is_authenticated and not request.user.is_superuser:
        return Response({'detail': 'Not superuser.'}, status=status.HTTP_403_FORBIDDEN)

    # Check object details
    try:
        obj_type = request.data['type']
    except KeyError:
        return Response({'detail': 'Object type was not provided.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        obj_id = request.data['id']
    except KeyError:
        return Response({'detail': 'Object ID was not provided.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check object type
    if obj_type.lower() == 'request':
        obj = Request.objects.get(pk=obj_id)
    elif obj_type.lower() == 'announcement':
        obj = Announcement.objects.get(pk=obj_id)
    elif obj_type.lower() == 'communityevent':
        obj = CommunityEvent.objects.get(pk=obj_id)
    elif obj_type.lower() == 'event':
        obj = Event.objects.get(pk=obj_id)
    elif obj_type.lower() == 'invitation':
        obj = Invitation.objects.get(pk=obj_id)
    else:
        return Response({'detail': 'Invalid object type.'}, status=status.HTTP_400_BAD_REQUEST)

    # Send mail notification
    send_mail_notification(users=(request.user,), obj=obj)

    return Response(
        {'detail': 'Mail notification sent to {}.'.format(get_email(request.user))}, status=status.HTTP_200_OK
    )
