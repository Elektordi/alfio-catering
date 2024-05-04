from django.db import models
from uuid import uuid4
import qrcode
import qrcode.image.svg


class Category(models.Model):
    name = models.CharField(max_length=100)
    background = models.FileField()

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Badge(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    key = models.UUIDField(default=uuid4, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    catering_guest = models.OneToOneField("catering.Guest", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = [['first_name', 'last_name']]

    def __str__(self):
        return "%s %s (%s)" % (self.first_name, self.last_name, self.title)

    def pdf(self):
        return "TODO"
