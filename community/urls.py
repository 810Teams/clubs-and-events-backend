from django.urls import path

from community.views import CreateClubView, RetrieveClubView, ListClubView, UpdateClubView, DeleteClubView

urlpatterns = [
    path('club/create/', CreateClubView.as_view(), name='create_club'),
    path('club/<int:pk>/', RetrieveClubView.as_view(), name='retrieve_club'),
    path('club/all/', ListClubView.as_view(), name='list_club'),
    path('club/<int:pk>/update', UpdateClubView.as_view(), name='update_club'),
    path('club/<int:pk>/delete', DeleteClubView.as_view(), name='delete_club'),
]