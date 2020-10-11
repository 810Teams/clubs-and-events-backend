from django.urls import path, include
from rest_framework.routers import DefaultRouter

from notification.views import NotificationViewSet, RequestNotificationViewSet, MembershipLogNotificationViewSet
from notification.views import AnnouncementNotificationViewSet, CommunityEventNotificationViewSet
from notification.views import EventNotificationViewSet


router = DefaultRouter()
router.register('notification/request', RequestNotificationViewSet)
router.register('notification/membership-log', MembershipLogNotificationViewSet)
router.register('notification/announcement', AnnouncementNotificationViewSet)
router.register('notification/community-event', CommunityEventNotificationViewSet)
router.register('notification/event', EventNotificationViewSet)
router.register('notification', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls))
]
