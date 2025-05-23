"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve

from api import api_alfio, api_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('alfio/', include(api_alfio.urls)),
    path('api/', include(api_admin.urls)),
    path('static/<path:path>', serve, kwargs={'document_root': settings.STATIC_ROOT}),
    path('media/<path:path>', serve, kwargs={'document_root': settings.MEDIA_ROOT}),
]
