'''
    Core Application URLs
    core/urls.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.views import get_datetime, get_settings


router = DefaultRouter()

urlpatterns = [
    path('datetime/', get_datetime),
    path('settings/', get_settings),
    path('', include(router.urls))
]
