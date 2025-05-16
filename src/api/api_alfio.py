from django.urls import path, include
from django.views.static import serve
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .serializers_alfio import DeviceSerializer, MealSerializer, StatsSerializer, TicketSerializer
from .models import Device
from catering.models import Meal, Guest, Registration, Check


class ApiKeyAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            auth = request.headers.get('Authorization')
            if not auth or not auth.startswith('ApiKey '):
                return False
            auth = auth.split('ApiKey ')[1]
            request.device = Device.objects.get(key=auth)
            if request.device:
                return True
        except Exception:
            pass
        return False


class UserDetailsView(APIView):
    permission_classes = [ApiKeyAccessPermission]

    def get(self, request, _format=None):
        return Response(DeviceSerializer(request.device).data)


class EventsView(APIView):
    permission_classes = [ApiKeyAccessPermission]

    def get(self, request, _format=None):
        meals = Meal.objects.all()
        serializer = MealSerializer(meals, many=True)
        return Response(serializer.data)


class StatsView(APIView):
    permission_classes = [ApiKeyAccessPermission]

    def get(self, request, pk, _format=None):
        meal = Meal.objects.get(id=pk)
        serializer = StatsSerializer(meal)
        return Response(serializer.data)


class CheckView(APIView):
    permission_classes = [ApiKeyAccessPermission]

    def post(self, request, pk, key, _format=None, override=False):
        meal = guest = reg = None
        try:
            meal = Meal.objects.get(id=pk)
            guest = Guest.objects.get(key=key)
            reg = Registration.objects.get(meal=meal, guest=guest)
            checked = reg.check_set.count()
            if checked >= reg.qty and not override:
                if guest.unlimited:
                    result = {"status": "MUST_PAY", "message": "Droits illimités. Confirmer dépassement ?", "dueAmount": 1, "currency": "+"}
                else:
                    result = {"status": "ALREADY_CHECK_IN", "message": "Droits épuisés."}
            else:
                Check(registration=reg).save()
                msg = "%s: %d/%d%s" % (guest.category, checked+1, reg.qty, "+" if guest.unlimited else "")
                result = {"status": "SUCCESS", "message": msg}
        except Meal.DoesNotExist:
            result = {"status": "EVENT_NOT_FOUND", "message": "Créneau inconnu"}
        except Guest.DoesNotExist:
            result = {"status": "TICKET_NOT_FOUND", "message": "Ticket inconnu"}
        except Registration.DoesNotExist:
            result = {"status": "INVALID_TICKET_STATE", "message": "Ticket invalide pour ce créneau"}

        if guest:
            guest = TicketSerializer(guest).data
        else:
            guest = {}

        if "message" in result:
            guest["categoryName"] = result["message"]
        return Response({"ticket": guest, "result": result})


class CheckConfirmView(CheckView):
    permission_classes = [ApiKeyAccessPermission]

    def post(self, request, pk, key, _format=None):
        return super().post(request, pk, key, _format, override=True)


api_urls = [
    path('user/details', UserDetailsView.as_view()),
    path('events', EventsView.as_view()),
    path('check-in/event/<int:pk>/statistics', StatsView.as_view()),
    path('check-in/event/<int:pk>/ticket/<str:key>', CheckView.as_view()),
    path('check-in/event/<int:pk>/ticket/<str:key>/confirm-on-site-payment', CheckConfirmView.as_view()),
]
urls = [
    path('admin/api/', include(api_urls)),
    path('static/<str:path>', serve, {"document_root": "%s/static" % (os.path.dirname(__file__))}),
]
