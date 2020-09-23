from django.urls import path, include
from rest_framework.routers import DefaultRouter

from community import views
from community.views import AllClubsView, ClubView, CreateClubView

urlpatterns = [
    path('club/all/', AllClubsView.as_view(), name='all_clubs'),
    path('club/create/', CreateClubView.as_view(), name='own_clubs'),
    path('club/<int:pk>/', ClubView.as_view(), name='club'),
]