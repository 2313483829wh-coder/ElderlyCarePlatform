from django.contrib import admin

from .models import ActivityRegistration, CommunityActivity, FamilyContact, MedicationPlan, ServiceOrder


@admin.register(FamilyContact)
class FamilyContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'elder', 'relation', 'phone', 'is_primary')
    search_fields = ('name', 'phone', 'elder__name')
    list_filter = ('relation', 'is_primary')


@admin.register(MedicationPlan)
class MedicationPlanAdmin(admin.ModelAdmin):
    list_display = ('medicine_name', 'elder', 'frequency', 'schedule_time', 'is_active')
    search_fields = ('medicine_name', 'elder__name')
    list_filter = ('is_active',)


@admin.register(CommunityActivity)
class CommunityActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'starts_at', 'is_active')
    search_fields = ('title', 'location')
    list_filter = ('is_active',)


@admin.register(ActivityRegistration)
class ActivityRegistrationAdmin(admin.ModelAdmin):
    list_display = ('activity', 'elder', 'status', 'created_at')
    search_fields = ('activity__title', 'elder__name')
    list_filter = ('status',)


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ('title', 'elder', 'request_type', 'service_kind', 'status', 'urgency', 'created_at')
    search_fields = ('title', 'elder__name', 'description')
    list_filter = ('request_type', 'service_kind', 'status', 'urgency')
