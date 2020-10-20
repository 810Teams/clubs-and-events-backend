from django.urls import path, include
from rest_framework.routers import DefaultRouter

from community.views import CommunityViewSet, ClubViewSet, LabViewSet, EventViewSet, CommunityEventViewSet


router = DefaultRouter()
router.register('lab', LabViewSet)
router.register('event/community', CommunityEventViewSet)
router.register('event', EventViewSet)
router.register('club', ClubViewSet)
router.register('', CommunityViewSet)

urlpatterns = [
    path('', include(router.urls))
]
