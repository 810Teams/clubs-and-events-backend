from django.urls import path

from category.views import AllClubTypesView, ClubTypeView, AllEventTypesView, EventTypeView, AllEventSeriesView, \
    EventSeriesView

urlpatterns = [
    path('type/club/', AllClubTypesView.as_view(), name='all_club_types'),
    path('type/club/<int:pk>/', ClubTypeView.as_view(), name='club_type'),
    path('type/event/', AllEventTypesView.as_view(), name='all_event_types'),
    path('type/event/<int:pk>/', EventTypeView.as_view(), name='event_type'),
    path('series/event', AllEventSeriesView.as_view(), name='all_event_series'),
    path('series/event/<int:pk>/', EventSeriesView.as_view(), name='event_series'),
]
