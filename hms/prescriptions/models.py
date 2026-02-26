"""Prescription models for Hospital Management System."""
from django.db import models
from accounts.models import Doctor, Patient
from appointments.models import Appointment


class Prescription(models.Model):
    """Prescription model linked to an appointment."""

    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name='prescription'
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='prescriptions'
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name='prescriptions'
    )
    diagnosis = models.TextField()
    symptoms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prescriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription #{self.id} - {self.patient.user.get_full_name()}"


class Medicine(models.Model):
    """Medicine model for prescriptions."""

    DOSE_CHOICES = [
        ('1-0-0', 'Morning'),
        ('0-1-0', 'Afternoon'),
        ('0-0-1', 'Night'),
        ('1-1-0', 'Morning & Afternoon'),
        ('1-0-1', 'Morning & Night'),
        ('0-1-1', 'Afternoon & Night'),
        ('1-1-1', 'Morning, Afternoon & Night'),
    ]

    prescription = models.ForeignKey(
        Prescription, on_delete=models.CASCADE, related_name='medicines'
    )
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=DOSE_CHOICES)
    duration = models.CharField(max_length=100)  # e.g., "7 days", "2 weeks"
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'medicines'
        ordering = ['id']

    def __str__(self):
        return f"{self.name} - {self.dosage}"
