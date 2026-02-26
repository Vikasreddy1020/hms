from django.contrib import admin
from .models import Prescription, Medicine


class MedicineInline(admin.TabularInline):
    model = Medicine
    extra = 1


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'appointment', 'follow_up_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'follow_up_date']
    search_fields = ['patient__user__username', 'doctor__user__username', 'diagnosis']
    inlines = [MedicineInline]


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'prescription', 'dosage', 'frequency', 'duration', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'prescription__patient__user__username']
