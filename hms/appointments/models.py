"""Appointment models for Hospital Management System."""
from django.db import models
from django.utils import timezone
from accounts.models import User, Doctor, Patient


class Appointment(models.Model):
    """Appointment model linking doctors and patients."""

    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='appointments'
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name='appointments'
    )
    appointment_date = models.DateTimeField()
    duration = models.PositiveIntegerField(default=30)  # in minutes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    reason = models.TextField()
    notes = models.TextField(blank=True)
    is_online = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appointments'
        ordering = ['appointment_date']
        indexes = [
            models.Index(fields=['appointment_date', 'status']),
            models.Index(fields=['patient', 'doctor']),
        ]

    def __str__(self):
        return f"Appointment #{self.id} - {self.patient.user.get_full_name()} with Dr. {self.doctor.user.get_full_name()}"

    @property
    def is_past(self):
        return self.appointment_date < timezone.now()

    @property
    def can_cancel(self):
        return self.status in ['scheduled', 'confirmed'] and not self.is_past

    @property
    def can_reschedule(self):
        return self.status in ['scheduled', 'confirmed'] and not self.is_past


class AppointmentSlot(models.Model):
    """Available time slots for doctors."""

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name='available_slots'
    )
    day_of_week = models.PositiveIntegerField(choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = 'appointment_slots'
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"Dr. {self.doctor.user.get_full_name()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
