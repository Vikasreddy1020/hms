"""Serializers for billing app."""
from rest_framework import serializers
from .models import Invoice, Payment
from accounts.serializers import PatientSerializer


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""

    class Meta:
        model = Payment
        fields = ['id', 'invoice', 'amount', 'payment_method', 'transaction_id', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    payments = PaymentSerializer(many=True, read_only=True)
    patient_details = PatientSerializer(source='patient', read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    appointment_details = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'appointment', 'appointment_details',
            'patient', 'patient_name', 'patient_details',
            'consultation_fee', 'medicine_cost', 'test_cost', 'other_charges',
            'discount', 'tax', 'total_amount', 'status', 'payment_method',
            'payment_date', 'notes', 'due_date', 'is_overdue', 'is_paid',
            'payments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'total_amount', 'created_at', 'updated_at']

    def get_appointment_details(self, obj):
        return {
            'id': obj.appointment.id,
            'date': obj.appointment.appointment_date,
            'doctor': obj.appointment.doctor.user.get_full_name(),
            'reason': obj.appointment.reason
        }


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating invoices."""

    class Meta:
        model = Invoice
        fields = ['appointment', 'patient', 'consultation_fee', 'medicine_cost',
                  'test_cost', 'other_charges', 'discount', 'tax', 'due_date', 'notes']


class InvoiceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating invoices."""

    class Meta:
        model = Invoice
        fields = ['status', 'payment_method', 'payment_date', 'notes', 'due_date']


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments."""

    class Meta:
        model = Payment
        fields = ['invoice', 'amount', 'payment_method', 'transaction_id', 'notes']
