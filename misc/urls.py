'''
    Miscellaneous Application URLs
    misc/urls.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from misc.views import FAQViewSet, VoteViewSet, MyVoteView, get_vote_info


router = DefaultRouter()
router.register('faq', FAQViewSet)
router.register('vote', VoteViewSet)

urlpatterns = [
    path('vote/me/', MyVoteView.as_view()),
    path('vote/info/', get_vote_info),
    path('', include(router.urls))
]
