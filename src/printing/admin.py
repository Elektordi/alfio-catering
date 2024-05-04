from django.contrib import admin, messages
from django.utils import timezone
from django.urls import reverse, path
from django.http import HttpResponse
from django.utils.html import format_html
from urllib.parse import quote

from .models import Category, Badge


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "title", "category"]
    ordering = ["first_name"]
    search_fields = ["first_name", "last_name", "title"]
    readonly_fields = ["key"]
    list_filter = ["category"]
    exclude = ["catering_guest"]
    actions = ["bulk_print"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        print_url = reverse("admin:badge_print", args=(obj.pk,))
        messages.add_message(request, messages.WARNING, format_html("<a href=\"{}\">Click here to print badge PDF</a>", quote(print_url)))

    def view_print(self, request, object_id, form_url='', extra_context=None):
        response = HttpResponse(b"TODO", content_type="application/pdf")
        return response

    def get_urls(self):
        return [
            path('<path:object_id>/print/', self.admin_site.admin_view(self.view_print), name="badge_print"),
        ] + super().get_urls()

    #@admin.action(description="Bulk-print selected badges")
    def bulk_print(modeladmin, request, queryset):
        response = HttpResponse(b"TODO", content_type="application/pdf")
        return response

