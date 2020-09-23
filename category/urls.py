from django.urls import path

from category.views import AllClubTypeView, ClubTypeView, AllEventTypeView, EventTypeView, AllEventSeriesView, \
    EventSeriesView

urlpatterns = [
    path('club/type/', AllClubTypeView.as_view(), name='all_club_type'),
    path('club/type/<int:pk>/', ClubTypeView.as_view(), name='club_type'),
    path('event/type/', AllEventTypeView.as_view(), name='all_event_type'),
    path('event/type/<int:pk>/', EventTypeView.as_view(), name='event_type'),
    path('event/series/', AllEventSeriesView.as_view(), name='all_event_series'),
    path('event/series/<int:pk>/', EventSeriesView.as_view(), name='event_series'),
]
