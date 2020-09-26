from django.urls import path, include
from rest_framework.routers import DefaultRouter

from asset.views import AnnouncementViewSet, AlbumViewSet, AlbumImageViewSet, CommentViewSet


router = DefaultRouter()
router.register('announcement', AnnouncementViewSet)
router.register('album/image', AlbumImageViewSet)
router.register('album', AlbumViewSet)
router.register('comment', CommentViewSet)

urlpatterns = [
    path('', include(router.urls))
]
