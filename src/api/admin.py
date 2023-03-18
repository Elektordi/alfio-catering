from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    # readonly_fields = ["key"]
    change_form_template = "admin/change_form_image.html"
