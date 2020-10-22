'''
    Generator Application URLs
    generator/urls.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from generator.views import QRCodeViewSet, JoinKeyViewSet, GeneratedDocxViewSet, generate_join_key, use_join_key


router = DefaultRouter()
router.register('qr-code', QRCodeViewSet)
router.register('join-key', JoinKeyViewSet)
router.register('docx', GeneratedDocxViewSet)

urlpatterns = [
    path('join-key/generate', generate_join_key),
    path('join-key/use', use_join_key),
    path('', include(router.urls))
]
