from rest_framework import serializers

from .models import Device


class DeviceSerializer(serializers.ModelSerializer):
    userType = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = ['description', 'userType']

    def get_userType(self, obj):
        return "OPERATOR"
