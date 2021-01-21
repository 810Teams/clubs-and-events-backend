'''
clubs_and_events URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
'''

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from clubs_and_events import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/asset/', include('asset.urls')),
    path('api/category/', include('category.urls')),
    path('api/community/', include('community.urls')),
    path('api/generator/', include('generator.urls')),
    path('api/membership/', include('membership.urls')),
    path('api/misc/', include('misc.urls')),
    path('api/notification/', include('notification.urls')),
    path('api/user/', include('user.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
