'''
    Category Application URLs
    category/urls.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from category.views import ClubTypeViewSet, EventTypeViewSet, EventSeriesViewSet


router = DefaultRouter()
router.register('club-type', ClubTypeViewSet)
router.register('event-type', EventTypeViewSet)
router.register('event-series', EventSeriesViewSet)

urlpatterns = [
    path('', include(router.urls))
]
