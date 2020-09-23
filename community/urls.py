from django.urls import path

from community.views import AllClubsView, ClubView, CreateClubView

urlpatterns = [
    path('club/all/', AllClubsView.as_view(), name='all_clubs'),
    path('club/create/', CreateClubView.as_view(), name='create_club'),
    path('club/<int:pk>/', ClubView.as_view(), name='club'),
]