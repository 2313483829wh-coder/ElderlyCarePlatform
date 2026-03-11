from django.contrib import admin
from .models import User, Elder


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'role', 'is_active', 'date_joined']
    search_fields = ['username', 'name']
    list_filter = ['role', 'is_active']


@admin.register(Elder)
class ElderAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'birth_date', 'community', 'phone', 'is_active']
    search_fields = ['name', 'id_card', 'phone']
    list_filter = ['community', 'gender', 'is_active']
    raw_id_fields = ['community']
