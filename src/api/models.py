from django.db import models
from uuid import uuid4
import json
import qrcode
import qrcode.image.svg
from django.conf import settings
import base64


class Device(models.Model):
    description = models.CharField(max_length=100)
    key = models.UUIDField(default=uuid4, unique=True)

    def __str__(self):
        return self.description

    def enroll_qrcode(self):
        url = "%s/alfio" % (settings.BASE_URL)
        data = json.dumps({"apiKey": str(self.key), "baseUrl": url})
        return qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage).to_string(encoding='unicode')
