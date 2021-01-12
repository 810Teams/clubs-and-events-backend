'''
    Miscellaneous Application URLs
    misc/urls.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from misc.views import FAQViewSet


router = DefaultRouter()
router.register('faq', FAQViewSet)

urlpatterns = [
    path('', include(router.urls))
]
