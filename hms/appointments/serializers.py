"""Serializers for appointments app."""
from rest_framework import serializers
from .models import Appointment, AppointmentSlot
from accounts.serializers import DoctorSerializer, PatientSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model."""
    patient_details = PatientSerializer(source='patient', read_only=True)
    doctor_details = DoctorSerializer(source='doctor', read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'patient_details',
            'doctor', 'doctor_name', 'doctor_details',
            'appointment_date', 'duration', 'status', 'reason', 'notes',
            'is_online', 'created_at', 'updated_at', 'is_past', 'can_cancel', 'can_reschedule'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'is_past', 'can_cancel', 'can_reschedule']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments."""

    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'appointment_date', 'duration', 'reason', 'is_online']

    def validate_appointment_date(self, value):
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError("Appointment date cannot be in the past")
        return value

    def validate(self, attrs):
        doctor = attrs.get('doctor')
        appointment_date = attrs.get('appointment_date')
        
        if doctor and appointment_date:
            # Check if doctor is available
            if not doctor.is_available:
                raise serializers.ValidationError({"doctor": "Doctor is not available"})
            
            # Check for conflicting appointments
            conflicting = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                status__in=['scheduled', 'confirmed']
            )
            if self.instance:
                conflicting = conflicting.exclude(pk=self.instance.pk)
            
            if conflicting.exists():
                raise serializers.ValidationError({"appointment_date": "This time slot is already booked"})
        
        return attrs


class AppointmentSlotSerializer(serializers.ModelSerializer):
    """Serializer for AppointmentSlot model."""
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)

    class Meta:
        model = AppointmentSlot
        fields = ['id', 'doctor', 'doctor_name', 'day_of_week', 'start_time', 'end_time', 'is_available']
        read_only_fields = ['id']


class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating appointment status."""

    class Meta:
        model = Appointment
        fields = ['status', 'notes']
