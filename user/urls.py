from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import UserViewSet, LoginAPIView, EmailPreferenceViewSet, MyUserView, MyEmailPreferenceView, \
    MyStudentCommitteeAuthorityView
from user.views import StudentCommitteeAuthorityViewSet


router = DefaultRouter()
router.register('user', UserViewSet)
router.register('email-preference', EmailPreferenceViewSet)
router.register('student-committee', StudentCommitteeAuthorityViewSet)


urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('user/me/', MyUserView.as_view()),
    path('email-preference/me/', MyEmailPreferenceView.as_view()),
    path('student-committee/me/', MyStudentCommitteeAuthorityView.as_view()),
    path('', include(router.urls))
]
