from django.contrib import admin
from .models import Checkup


@admin.register(Checkup)
class CheckupAdmin(admin.ModelAdmin):
    list_display = ['elder', 'year', 'sequence', 'check_date', 'hospital', 'overall_result']
    search_fields = ['elder__name', 'hospital']
    list_filter = ['year', 'sequence', 'check_date']
    raw_id_fields = ['elder']
    date_hierarchy = 'check_date'
