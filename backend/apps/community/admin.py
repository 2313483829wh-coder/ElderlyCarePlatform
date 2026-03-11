from django.contrib import admin
from .models import Community


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'contact_person', 'contact_phone', 'created_at']
    search_fields = ['name', 'address', 'contact_person']
    list_filter = ['created_at']
