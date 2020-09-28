from django.urls import path, include
from rest_framework.routers import DefaultRouter

from membership.views import RequestViewSet, InvitationViewSet, MembershipViewSet


router = DefaultRouter()
router.register('request', RequestViewSet)
router.register('invitation', InvitationViewSet)
router.register('membership', MembershipViewSet)

urlpatterns = [
    path('', include(router.urls))
]
