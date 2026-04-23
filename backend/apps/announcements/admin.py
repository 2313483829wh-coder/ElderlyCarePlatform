from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'audience', 'is_active', 'is_pinned', 'publish_at')
    list_filter = ('category', 'audience', 'is_active', 'is_pinned')
    search_fields = ('title', 'summary', 'content')
