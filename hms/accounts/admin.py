from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Doctor, Patient


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active']
    list_filter = ['role', 'is_verified', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'address', 'date_of_birth', 'profile_picture', 'is_verified')}),
    )


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'qualification', 'experience_years', 'is_available']
    list_filter = ['specialization', 'is_available']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'license_number']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'blood_group', 'gender', 'insurance_number']
    list_filter = ['blood_group', 'gender']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'insurance_number']
