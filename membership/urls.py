from django.urls import path, include
from rest_framework.routers import DefaultRouter

from membership.views import RequestViewSet, InvitationViewSet


router = DefaultRouter()
router.register('request', RequestViewSet)
router.register('invitation', InvitationViewSet)

urlpatterns = [
    path('', include(router.urls))
]
