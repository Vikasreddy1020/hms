from django.contrib import admin
from .models import DashboardCache


@admin.register(DashboardCache)
class DashboardCacheAdmin(admin.ModelAdmin):
    list_display = ['cache_key', 'expires_at', 'created_at']
    search_fields = ['cache_key']
    readonly_fields = ['created_at']
