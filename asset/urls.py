from django.urls import path, include
from rest_framework.routers import DefaultRouter

from asset.views import AnnouncementViewSet

router = DefaultRouter()
router.register('announcement', AnnouncementViewSet)

urlpatterns = [
    path('', include(router.urls))
]