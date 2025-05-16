from django.contrib import admin, messages
from django.shortcuts import redirect
from django.utils import timezone
from .models import Guest, Meal, Registration


class RegistrationInline(admin.TabularInline):
    model = Registration
    ordering = ["meal__name"]
    fields = ["meal", "qty", "checked_qty", "checks"]
    readonly_fields = ["checked_qty", "checks"]

    def checked_qty(self, obj):
        return obj.check_set.count()

    def checks(self, obj):
        return "\n".join([timezone.localtime(x.time).isoformat() for x in obj.check_set.all()])


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "unlimited"]
    ordering = ["name"]
    list_filter = ["category"]
    search_fields = ["name"]
    change_form_template = "admin/change_form_image.html"
    inlines = [RegistrationInline]
    actions = ["add_all_meals"]

    #@admin.action(description="Add all meals (1 for each)")
    def add_all_meals(modeladmin, request, queryset):
        for obj in queryset:
            for m in Meal.objects.all():
                Registration.objects.get_or_create(guest=obj, meal=m, defaults={"qty": 1})
        messages.add_message(request, messages.SUCCESS, "Registred to all meals.")
        return redirect(request.path)


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ["name", "start", "end", "planned_qty", "checked_qty"]
    ordering = ["start"]
    search_fields = ["name"]
    #readonly_fields = ["planned_qty", "checked_qty"]
    readonly_fields = ["checked_qty"]
