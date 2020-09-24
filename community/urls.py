from django.urls import path, include
from rest_framework.routers import DefaultRouter

from community.views import ClubViewSet

router = DefaultRouter()
router.register('club', ClubViewSet)

urlpatterns = [
    path('', include(router.urls))
]