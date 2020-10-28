'''
    Community Application URLs
    community/urls.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from community.views import CommunityViewSet, ClubViewSet, EventViewSet, CommunityEventViewSet, LabViewSet


router = DefaultRouter()
router.register('lab', LabViewSet)
router.register('event/community', CommunityEventViewSet)
router.register('event', EventViewSet)
router.register('club', ClubViewSet)
router.register('community', CommunityViewSet)

urlpatterns = [
    path('', include(router.urls))
]
