from rest_framework import serializers
from django.utils import timezone

from .models import Device
from catering.models import Meal


class DeviceSerializer(serializers.ModelSerializer):
    userType = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = ['description', 'userType']

    def get_userType(self, obj):
        return "OPERATOR"


class MealSerializer(serializers.ModelSerializer):
    key = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    begin = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    timezone = serializers.SerializerMethodField()
    imageUrl = serializers.SerializerMethodField()

    class Meta:
        model = Meal
        fields = ['name', 'key', 'url', 'begin', 'end', 'timezone', 'imageUrl']

    def get_key(self, obj):
        return str(obj.id)

    def get_url(self, obj):
        return "/event/%d" % (obj.id)

    def get_begin(self, obj):
        return obj.start.isoformat()

    def get_end(self, obj):
        return obj.end.isoformat()

    def get_timezone(self, obj):
        return timezone.get_current_timezone_name()

    def get_imageUrl(self, obj):
        return "/static/pixel.png"


class StatsSerializer(serializers.ModelSerializer):
    totalAttendees = serializers.SerializerMethodField()
    checkedIn = serializers.SerializerMethodField()
    lastUpdate = serializers.SerializerMethodField()

    class Meta:
        model = Meal
        fields = ['totalAttendees', 'checkedIn', 'lastUpdate']

    def get_totalAttendees(self, obj):
        return obj.planned_qty

    def get_checkedIn(self, obj):
        return obj.checked_qty

    def get_lastUpdate(self, _obj):
        return int(timezone.now().timestamp())
