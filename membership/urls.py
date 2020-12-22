'''
    Membership Application URLs
    membership/urls.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from membership.views import RequestViewSet, InvitationViewSet, MembershipViewSet, CustomMembershipLabelViewSet
from membership.views import MembershipLogViewSet, AdvisoryViewSet, ApprovalRequestViewSet
from membership.views import get_membership_default_labels, get_past_memberships


router = DefaultRouter()
router.register('request', RequestViewSet)
router.register('invitation', InvitationViewSet)
router.register('membership/label/custom', CustomMembershipLabelViewSet)
router.register('membership/log', MembershipLogViewSet)
router.register('membership', MembershipViewSet)
router.register('advisory', AdvisoryViewSet)
router.register('approval-request', ApprovalRequestViewSet)

urlpatterns = [
    path('membership/label/default/', get_membership_default_labels),
    path('membership/past/<int:user_id>/', get_past_memberships),
    path('', include(router.urls))
]
