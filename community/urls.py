from django.urls import path

from community import views

urlpatterns = [
    path('', views.api_overview, name='api_overview'),
    path('clubs/', views.get_clubs, name='get_clubs'),
]