from django.urls import path, include
from rest_framework.routers import DefaultRouter

from community import views
from community.views import OwnClubsView

urlpatterns = [
    path('club/', OwnClubsView.as_view(), name='clubs')
]