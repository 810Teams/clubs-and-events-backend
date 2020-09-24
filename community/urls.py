from django.urls import path, include
from rest_framework.routers import DefaultRouter

from community.views import ClubViewSet, LabViewSet

router = DefaultRouter()
router.register('club', ClubViewSet)
router.register('lab', LabViewSet)

urlpatterns = [
    path('', include(router.urls))
]