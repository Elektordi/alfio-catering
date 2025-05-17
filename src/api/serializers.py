from rest_framework import serializers
from django.utils import timezone

from catering.models import Meal, Guest, Registration
from printing.models import Badge, Category


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
    registrations = RegistrationSerializer(many=True)

    def create(self, validated_data):
        return self.update(Guest(), validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if not isinstance(value, (list, dict)):
                setattr(instance, attr, value)

        instance.save()

        registrations = {x.meal.id: x for x in instance.registrations.all()}
        for l in validated_data['registrations']:
            if l['qty'] == 0:
                continue
            if l['meal'].id in registrations:
                r = registrations.pop(l['meal'].id)
            else:
                r = Registration(guest=instance, meal=l['meal'])
            if not r.id or r.qty != l['qty']:
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


class BadgeSerializer(serializers.ModelSerializer):
    catering_guest = GuestSerializer()

    def create(self, validated_data):
        return self.update(Badge(), validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if not isinstance(value, (list, dict)):
                setattr(instance, attr, value)

        if validated_data['catering_guest']:
            if not instance.catering_guest:
                instance.catering_guest = Guest(key=instance.key)
            GuestSerializer.update(self, instance.catering_guest, validated_data['catering_guest'])

        instance.save()
        return instance


    class Meta:
        model = Badge
        fields = ['id', 'first_name', 'last_name', 'title', 'category', 'key', 'catering_guest']

