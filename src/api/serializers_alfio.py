from rest_framework import serializers
from django.utils import timezone

from .models import Device
from catering.models import Meal, Guest, Registration


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
    begin = serializers.DateTimeField(source="start")
    end = serializers.DateTimeField()
    timezone = serializers.SerializerMethodField()
    imageUrl = serializers.SerializerMethodField()

    class Meta:
        model = Meal
        fields = ['name', 'key', 'url', 'begin', 'end', 'timezone', 'imageUrl']

    def get_key(self, obj):
        return str(obj.id)

    def get_url(self, obj):
        return "/event/%d" % (obj.id)

    def get_timezone(self, obj):
        return timezone.get_current_timezone_name()

    def get_imageUrl(self, obj):
        return "/static/pixel.png"


class StatsSerializer(serializers.ModelSerializer):
    totalAttendees = serializers.IntegerField(source="planned_qty")
    checkedIn = serializers.IntegerField(source="checked_qty")
    lastUpdate = serializers.SerializerMethodField()

    class Meta:
        model = Meal
        fields = ['totalAttendees', 'checkedIn', 'lastUpdate']

    def get_lastUpdate(self, _obj):
        return int(timezone.now().timestamp())


class TicketSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(source='key')
    status = serializers.SerializerMethodField()
    fullName = serializers.CharField(source='name')
    categoryName = serializers.CharField(source='category')

    class Meta:
        model = Guest
        fields = ['id', 'uuid', 'status', 'fullName', 'categoryName']

    def get_status(self, _obj):
        return "OK"
