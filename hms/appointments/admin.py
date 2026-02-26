from django.contrib import admin
from .models import Appointment, AppointmentSlot


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'appointment_date', 'status', 'is_online']
    list_filter = ['status', 'is_online', 'appointment_date']
    search_fields = ['patient__user__username', 'doctor__user__username', 'reason']
    date_hierarchy = 'appointment_date'


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available']
    search_fields = ['doctor__user__username']
