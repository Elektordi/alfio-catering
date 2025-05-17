from rest_framework import serializers
from django.utils import timezone

from catering.models import Meal, Guest, Registration


class MealSerializer(serializers.ModelSerializer):
    checked_qty = serializers.ReadOnlyField()

    class Meta:
        model = Meal
        fields = ['id', 'name', 'start', 'end', 'planned_qty', 'checked_qty']


class RegistrationSerializer(serializers.ModelSerializer):
    #meal = MealSerializer()

    class Meta:
        model = Registration
        fields = ['meal', 'qty']


class GuestSerializer(serializers.ModelSerializer):
    registrations = RegistrationSerializer(many=True, source='registration_set')

    def create(self, validated_data):
        return self.update(Guest(), validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if not type(value) is list:
                setattr(instance, attr, value)

        instance.save()

        registrations = {x.meal.id: x for x in instance.registration_set.all()}
        for l in validated_data['registration_set']:
            if l['qty'] == 0:
                continue
            if l['meal'].id in registrations:
                r = registrations.pop(l['meal'].id)
            else:
                r = Registration(guest=instance, meal=l['meal'])
            if r.qty != l['qty']:
                r.qty = l['qty']
                r.save()

        for missing in registrations:
            r = registrations[missing]
            if r.checks.exists():
                r.qty = 0
                r.save()
            else:
                r.delete()

        return instance

    class Meta:
        model = Guest
        fields = ['id', 'name', 'category', 'key', 'registrations']
        validators = []
