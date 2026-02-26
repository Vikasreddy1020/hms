"""Dashboard models for Hospital Management System."""
from django.db import models


class DashboardCache(models.Model):
    """Model to store dashboard cache metadata."""

    cache_key = models.CharField(max_length=100, unique=True)
    data = models.JSONField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dashboard_cache'

    def __str__(self):
        return f"Cache: {self.cache_key}"
