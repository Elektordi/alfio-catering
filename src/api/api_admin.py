from django.urls import path
from django.http import Http404
from django.core.exceptions import ValidationError

from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet

from .serializers import MealSerializer, GuestSerializer
from catering.models import Meal, Guest


class StrictDjangoModelPermissions(DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class MealsViewSet(ModelViewSet):
    permission_classes = [StrictDjangoModelPermissions]
    queryset = Meal.objects.all()
    serializer_class = MealSerializer


class GuestsViewSet(ModelViewSet):
    permission_classes = [StrictDjangoModelPermissions]
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

    @action(detail=False, url_path='key/(?P<key>[^/.]+)')
    def key(self, request, key):
        try:
            obj = Guest.objects.get(key=key)
        except (ValueError, ValidationError, Guest.DoesNotExist):
            raise Http404("Invalid key")
        serializer = self.get_serializer(obj, many=False)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def sync(self, request):
        if not type(request.data) is list:
            raise ParseError()
        out = []
        for entry in request.data:
            try:
                if "id" in entry:
                    guest = Guest.objects.get(id=entry['id'])
                elif "key" in entry:
                    guest = Guest.objects.get(key=entry['key'])
                else:
                    guest = None
            except (ValueError, ValidationError, Guest.DoesNotExist):
                guest = None

            serializer = GuestSerializer(guest, data=entry)
            if serializer.is_valid():
                serializer.save()
                out.append(serializer.data)
            else:
                out.append({"errors":serializer.errors})
        return Response(out)


router = DefaultRouter()
router.register('meals', MealsViewSet, basename='meal')
router.register('guests', GuestsViewSet, basename='guest')
urls = router.urls
