from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['elder', 'alert_type', 'level', 'title', 'status', 'created_at']
    search_fields = ['elder__name', 'title', 'detail']
    list_filter = ['alert_type', 'level', 'status', 'created_at']
    raw_id_fields = ['elder']
    date_hierarchy = 'created_at'
