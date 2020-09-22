from django.urls import path

from community import views

urlpatterns = [
    path('', views.api_overview, name='api_overview'),
    path('clubs/get', views.get_clubs, name='get_clubs'),
]