from django.urls import path, include
from rest_framework.routers import DefaultRouter

from generator.views import QRCodeViewSet, JoinKeyViewSet, generate_join_key, use_join_key


router = DefaultRouter()
router.register('qr-code', QRCodeViewSet)
router.register('join-key', JoinKeyViewSet)

urlpatterns = [
    path('join-key/generate', generate_join_key),
    path('join-key/use/<str:key>', use_join_key),
    path('', include(router.urls))
]
