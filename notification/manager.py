from asset.models import Announcement
from community.models import CommunityEvent, Event
from membership.models import Request, MembershipLog
from notification.models import Notification, RequestNotification, MembershipLogNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification


class InvalidNotificationType(Exception):
    pass


def notify(user, obj=None):
    if isinstance(obj, Request):
        RequestNotification.objects.create(user=user, request=obj)
    elif isinstance(obj, MembershipLog):
        MembershipLogNotification.objects.create(user=user, request=obj)
    elif isinstance(obj, Announcement):
        AnnouncementNotification.objects.create(user=user, request=obj)
    elif isinstance(obj, CommunityEvent):
        CommunityEventNotification.objects.create(user=user, request=obj)
    elif isinstance(obj, Event):
        EventNotification.objects.create(user=user, request=obj)
    else:
        raise InvalidNotificationType
