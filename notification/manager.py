from notification.models import Notification, RequestNotification, JoinNotification, RemovedNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification


class InvalidNotificationType(Exception):
    pass


def notify(user, notification_type=None, obj=None):
    if notification_type == 'request':
        RequestNotification.objects.create(user=user, request=obj)
    elif notification_type == 'join':
        JoinNotification.objects.create(user=user, request=obj)
    elif notification_type == 'removed':
        RemovedNotification.objects.create(user=user, request=obj)
    elif notification_type == 'announcement':
        AnnouncementNotification.objects.create(user=user, request=obj)
    elif notification_type == 'community_event':
        CommunityEventNotification.objects.create(user=user, request=obj)
    elif notification_type == 'event':
        EventNotification.objects.create(user=user, request=obj)
    else:
        raise InvalidNotificationType
