from django.urls import path, include
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import DeviceSerializer
from .models import Device


class UserDetailsView(APIView):
    def get(self, request, _format=None):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('ApiKey '):
            return Response(status=status.HTTP_403_FORBIDDEN)
        auth = auth.split('ApiKey ')[1]
        device = Device.objects.get(key=auth)
        return Response(DeviceSerializer(device).data)


class EventsView(APIView):
    def get(self, request, _format=None):
        return Response([])


api_urls = [
    path('user/details', UserDetailsView.as_view()),
    path('events', EventsView.as_view()),
]
urls = [path('admin/api/', include(api_urls))]
