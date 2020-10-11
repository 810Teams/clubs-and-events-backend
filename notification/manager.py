from asset.models import Announcement
from community.models import CommunityEvent, Event
from membership.models import Request, MembershipLog
from notification.models import Notification, RequestNotification, MembershipLogNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification


class InvalidNotificationType(Exception):
    pass


def notify(users, obj=None):
    for i in users:
        if isinstance(obj, Request):
            RequestNotification.objects.create(user=i, request=obj)
        elif isinstance(obj, MembershipLog):
            MembershipLogNotification.objects.create(user=i, request=obj)
        elif isinstance(obj, Announcement):
            AnnouncementNotification.objects.create(user=i, request=obj)
        elif isinstance(obj, CommunityEvent):
            CommunityEventNotification.objects.create(user=i, request=obj)
        elif isinstance(obj, Event):
            EventNotification.objects.create(user=i, request=obj)
        else:
            raise InvalidNotificationType
