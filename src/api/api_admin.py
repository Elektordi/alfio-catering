from django.urls import path
from django.http import Http404
from django.core.exceptions import ValidationError

from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet

from .serializers import MealSerializer, GuestSerializer, BadgeSerializer
from catering.models import Meal, Guest
from printing.models import Badge


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


class SyncModelViewSet(ModelViewSet):
    permission_classes = [StrictDjangoModelPermissions]

    @action(detail=False, url_path='key/(?P<key>[^/.]+)')
    def key(self, request, key):
        model = self.get_queryset().model
        try:
            obj = self.get_queryset().get(key=key)
        except (ValueError, ValidationError, model.DoesNotExist):
            raise Http404("Invalid key")
        serializer = self.get_serializer(obj, many=False)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def sync(self, request):
        if not type(request.data) is list:
            raise ParseError()
        model = self.get_queryset().model
        out = []
        for entry in request.data:
            try:
                if "id" in entry:
                    obj = self.get_queryset().get(id=entry['id'])
                elif "key" in entry:
                    obj = self.get_queryset().get(key=entry['key'])
                else:
                    obj = None
            except (ValueError, ValidationError, model.DoesNotExist):
                obj = None

            serializer = self.get_serializer(obj, data=entry)
            if serializer.is_valid():
                serializer.save()
                out.append(serializer.data)
            else:
                out.append({"errors":serializer.errors})
        return Response(out)


class GuestsViewSet(SyncModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class BadgesViewSet(SyncModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer


router = DefaultRouter()
router.register('meals', MealsViewSet, basename='meal')
router.register('guests', GuestsViewSet, basename='guest')
router.register('badges', BadgesViewSet, basename='badge')
urls = router.urls
