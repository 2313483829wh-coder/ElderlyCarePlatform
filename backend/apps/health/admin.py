from django.contrib import admin
from .models import DailyHealth


@admin.register(DailyHealth)
class DailyHealthAdmin(admin.ModelAdmin):
    list_display = ['elder', 'date', 'heart_rate', 'blood_oxygen', 'systolic_bp', 'diastolic_bp', 'temperature', 'submitted_at']
    search_fields = ['elder__name']
    list_filter = ['date', 'submitted_at']
    raw_id_fields = ['elder']
    date_hierarchy = 'date'
