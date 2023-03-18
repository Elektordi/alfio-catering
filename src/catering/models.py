from django.db import models
from uuid import uuid4
import qrcode
import qrcode.image.svg
from django.db.models import Sum


class Guest(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    key = models.UUIDField(default=uuid4, unique=True)
    unlimited = models.BooleanField()

    def __str__(self):
        return self.name

    def qrcode(self):
        data = str(self.key)
        return qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage).to_string(encoding='unicode')


class Meal(models.Model):
    name = models.CharField(max_length=100)
    start = models.DateTimeField()
    end = models.DateTimeField()
    planned_qty = models.PositiveSmallIntegerField(default=0)
    checked_qty = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class Registration(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    qty = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = [['guest', 'meal']]

    def __str__(self):
        return "[%s] %s = %d repas" % (self.meal, self.guest, self.qty)

    def save(self, **kwargs):
        super().save(**kwargs)
        meal = self.meal
        meal.planned_qty = Registration.objects.filter(meal=self.meal).aggregate(Sum('qty'))['qty__sum']
        meal.save()


class Check(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.PROTECT)
    time = models.DateTimeField(auto_now_add=True)

    def save(self, **kwargs):
        super().save(**kwargs)
        meal = self.registration.meal
        meal.checked_qty = Check.objects.filter(registration__meal=self.registration.meal).count()
        meal.save()
