"""Serializers for prescriptions app."""
from rest_framework import serializers
from .models import Prescription, Medicine
from accounts.serializers import DoctorSerializer, PatientSerializer


class MedicineSerializer(serializers.ModelSerializer):
    """Serializer for Medicine model."""

    class Meta:
        model = Medicine
        fields = ['id', 'name', 'dosage', 'frequency', 'duration', 'instructions', 'is_active']
        read_only_fields = ['id']


class PrescriptionSerializer(serializers.ModelSerializer):
    """Serializer for Prescription model."""
    medicines = MedicineSerializer(many=True, read_only=True)
    patient_details = PatientSerializer(source='patient', read_only=True)
    doctor_details = DoctorSerializer(source='doctor', read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'appointment', 'patient', 'patient_name', 'patient_details',
            'doctor', 'doctor_name', 'doctor_details', 'diagnosis', 'symptoms',
            'notes', 'follow_up_date', 'is_active', 'medicines',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'doctor', 'created_at', 'updated_at']


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating prescriptions with medicines."""
    medicines = MedicineSerializer(many=True)

    class Meta:
        model = Prescription
        fields = ['appointment', 'patient', 'diagnosis', 'symptoms', 'notes', 'follow_up_date', 'medicines']

    def create(self, validated_data):
        medicines_data = validated_data.pop('medicines')
        prescription = Prescription.objects.create(**validated_data)
        
        for medicine_data in medicines_data:
            Medicine.objects.create(prescription=prescription, **medicine_data)
        
        return prescription


class PrescriptionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating prescriptions."""
    medicines = MedicineSerializer(many=True)

    class Meta:
        model = Prescription
        fields = ['diagnosis', 'symptoms', 'notes', 'follow_up_date', 'is_active', 'medicines']

    def update(self, instance, validated_data):
        medicines_data = validated_data.pop('medicines', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if medicines_data is not None:
            instance.medicines.all().delete()
            for medicine_data in medicines_data:
                Medicine.objects.create(prescription=instance, **medicine_data)
        
        return instance
