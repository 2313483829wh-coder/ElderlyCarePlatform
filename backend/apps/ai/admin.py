from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['elder', 'title', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['elder__name', 'title']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'content_preview', 'created_at']
    list_filter = ['role']

    def content_preview(self, obj):
        return (obj.content[:80] + '...') if len(obj.content) > 80 else obj.content
    content_preview.short_description = '内容预览'
