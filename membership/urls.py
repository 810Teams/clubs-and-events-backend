from django.urls import path, include
from rest_framework.routers import DefaultRouter

from membership.views import RequestViewSet, InvitationViewSet, MembershipViewSet, CustomMembershipLabelViewSet
from membership.views import MembershipLogViewSet, AdvisoryViewSet


router = DefaultRouter()
router.register('request', RequestViewSet)
router.register('invitation', InvitationViewSet)
router.register('custom-label', CustomMembershipLabelViewSet)
router.register('membership/log', MembershipLogViewSet)
router.register('membership', MembershipViewSet)
router.register('advisory', AdvisoryViewSet)

urlpatterns = [
    path('', include(router.urls))
]
