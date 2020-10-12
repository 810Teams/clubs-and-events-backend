from asset.models import Announcement
from community.models import CommunityEvent, Event
from membership.models import Request, MembershipLog
from notification.models import RequestNotification, MembershipLogNotification
from notification.models import AnnouncementNotification, CommunityEventNotification, EventNotification


class InvalidNotificationType(Exception):
    pass


def notify(users=tuple(), obj=None):
    for i in users:
        if isinstance(obj, Request):
            RequestNotification.objects.create(user_id=i.id, request_id=obj.id)
        elif isinstance(obj, MembershipLog):
            MembershipLogNotification.objects.create(user_id=i.id, membership_log=obj.id)
        elif isinstance(obj, Announcement):
            AnnouncementNotification.objects.create(user_id=i.id, announcement_id=obj.id)
        elif isinstance(obj, CommunityEvent):
            CommunityEventNotification.objects.create(user_id=i.id, community_event_id=obj.id)
        elif isinstance(obj, Event):
            EventNotification.objects.create(user_id=i.id, event_id=obj.id)
        else:
            raise InvalidNotificationType
