from django.urls import path, include
from django.views.static import serve
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import DeviceSerializer, MealSerializer, StatsSerializer
from .models import Device
from catering.models import Meal, Guest, Registration, Check


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
        meals = Meal.objects.all()
        serializer = MealSerializer(meals, many=True)
        return Response(serializer.data)


class StatsView(APIView):
    def get(self, request, pk, _format=None):
        meal = Meal.objects.get(id=pk)
        serializer = StatsSerializer(meal)
        return Response(serializer.data)


class CheckView(APIView):
    def post(self, request, pk, key, _format=None):
        meal = Meal.objects.get(id=pk)
        guest = Guest.objects.get(key=key)
        reg = Registration.objects.get(meal=meal, guest=guest)
        checked = reg.check_set.count()
        if checked >= reg.qty:
            if guest.unlimited:
                return Response({})
            else:
                return Response({})
        Check(registration=reg).save()
        return Response({})


api_urls = [
    path('user/details', UserDetailsView.as_view()),
    path('events', EventsView.as_view()),
    path('check-in/event/<int:pk>/statistics', StatsView.as_view()),
    path('check-in/event/<int:pk>/ticket/<str:key>', CheckView.as_view()),
]
urls = [
    path('admin/api/', include(api_urls)),
    path('static/<str:path>', serve, {"document_root": "%s/static" % (os.path.dirname(__file__))}),
]
