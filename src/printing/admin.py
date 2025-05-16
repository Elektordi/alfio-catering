from django.contrib import admin, messages
from django.utils import timezone
from django.urls import reverse, path
from django.http import HttpResponse
from django.utils.html import format_html
from django.shortcuts import redirect
from urllib.parse import quote
import qrcode
import qrcode.image.svg

from .models import Category, Badge
from catering.models import Guest


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "title", "category", "catering_exists", "created_at"]
    ordering = ["first_name"]
    search_fields = ["first_name", "last_name", "title"]
    readonly_fields = ["key", "catering_guest", "created_at", "updated_at"]
    list_filter = ["category"]
    actions = ["bulk_print", "create_catering"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        print_url = reverse("admin:badge_print", args=(obj.pk,))
        messages.add_message(request, messages.WARNING, format_html("<a href=\"{}\">Click here to print badge PDF</a>", quote(print_url)))

    def view_print(self, request, object_id, form_url='', extra_context=None):
        obj = Badge.objects.get(id=object_id)
        response = HttpResponse(obj.pdf().write_pdf(), content_type="application/pdf")
        return response

    def get_urls(self):
        return [
            path('<path:object_id>/print/', self.admin_site.admin_view(self.view_print), name="badge_print"),
        ] + super().get_urls()

    def catering_exists(self, obj):
        return not obj.catering_guest is None

    #@admin.action(description="Bulk-print selected badges")
    def bulk_print(modeladmin, request, queryset):
        docs = []
        for obj in queryset:
            docs.append(obj.pdf())
        if not docs:
            messages.add_message(request, messages.ERROR, "No pages to print.")
            return redirect(request.path)
        doc = docs[0].copy([p for d in docs for p in d.pages])
        response = HttpResponse(doc.write_pdf(), content_type="application/pdf")
        return response

    #@admin.action(description="Create catering guests")
    def create_catering(modeladmin, request, queryset):
        for obj in queryset:
            name = "%s %s" % (obj.first_name, obj.last_name)
            if obj.catering_guest:
                guest = obj.catering_guest
            else:
                guest = Guest.objects.filter(name=name).first()
                if not guest:
                    guest = Guest(unlimited=False)
            guest.name = name
            guest.category = obj.category.name
            guest.key = obj.key
            guest.save()
            obj.catering_guest = guest
            obj.save()
        messages.add_message(request, messages.SUCCESS, "Catering created/updated.")
        return redirect(request.path)

