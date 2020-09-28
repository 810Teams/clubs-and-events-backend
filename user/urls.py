from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import UserViewSet, LoginAPIView, EmailPreferenceViewSet

router = DefaultRouter()
router.register('user/email-preference', EmailPreferenceViewSet)
router.register('user', UserViewSet)

urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('', include(router.urls))
]
