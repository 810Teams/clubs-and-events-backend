'''
    Community Application URLs
    community/urls.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from community.views import CommunityViewSet, ClubViewSet, EventViewSet, CommunityEventViewSet, LabViewSet
from community.views import MyCommunityView, MyClubView, MyEventView, MyCommunityEventView, MyLabView


router = DefaultRouter()
router.register('community', CommunityViewSet)
router.register('club', ClubViewSet)
router.register('event/community', CommunityEventViewSet)
router.register('event', EventViewSet)
router.register('lab', LabViewSet)

urlpatterns = [
    path('community/me/', MyCommunityView.as_view()),
    path('club/me/', MyClubView.as_view()),
    path('event/me/', MyEventView.as_view()),
    path('event/community/me/', MyCommunityEventView.as_view()),
    path('lab/me/', MyLabView.as_view()),
    path('', include(router.urls))
]
