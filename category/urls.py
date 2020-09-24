from django.urls import path, include
from rest_framework.routers import DefaultRouter

from category.views import ClubTypeViewSet, EventTypeViewSet, EventSeriesViewSet

router = DefaultRouter()
router.register('type/club', ClubTypeViewSet)
router.register('type/event', EventTypeViewSet)
router.register('series/event', EventSeriesViewSet)

urlpatterns = [
    path('', include(router.urls))
]
