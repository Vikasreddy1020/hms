"""Billing models for Hospital Management System."""
from django.db import models
from accounts.models import Patient
from appointments.models import Appointment


class Invoice(models.Model):
    """Invoice model linked to an appointment."""

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )

    invoice_number = models.CharField(max_length=20, unique=True)
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name='invoice'
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='invoices'
    )
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    medicine_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    test_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.patient.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number.replace('INV-', ''))
                self.invoice_number = f"INV-{str(last_number + 1).zfill(6)}"
            else:
                self.invoice_number = "INV-000001"
        
        subtotal = self.consultation_fee + self.medicine_cost + self.test_cost + self.other_charges
        self.total_amount = subtotal - self.discount + self.tax
        
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.due_date and self.status == 'pending':
            from django.utils import timezone
            return self.due_date < timezone.now().date()
        return False

    @property
    def is_paid(self):
        return self.status == 'paid'


class Payment(models.Model):
    """Payment records for invoices."""

    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('bank_transfer', 'Bank Transfer'),
        ('insurance', 'Insurance'),
    )

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment #{self.id} - {self.invoice.invoice_number}"
