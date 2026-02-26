"""Views for billing app."""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.db.models import Sum, Q
from django.utils import timezone
from .models import Invoice, Payment
from .serializers import (
    InvoiceSerializer, InvoiceCreateSerializer, InvoiceUpdateSerializer,
    PaymentSerializer, PaymentCreateSerializer
)
from accounts.permissions import IsAdminUser, IsDoctor, IsPatient, IsOwnerOrAdmin


class InvoiceListView(generics.ListCreateAPIView):
    """API endpoint to list or create invoices."""
    queryset = Invoice.objects.select_related('patient__user', 'appointment__doctor__user').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InvoiceCreateSerializer
        return InvoiceSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_patient:
            queryset = queryset.filter(patient__user=user)
        
        # Additional filters
        status_filter = self.request.query_params.get('status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update or delete an invoice."""
    queryset = Invoice.objects.select_related(
        'patient__user', 'appointment__doctor__user'
    ).prefetch_related('payments').all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return InvoiceUpdateSerializer
        return InvoiceSerializer


class MyInvoicesView(generics.ListAPIView):
    """API endpoint to get current patient's invoices."""
    serializer_class = InvoiceSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return Invoice.objects.filter(
            patient__user=self.request.user
        ).select_related('patient__user', 'appointment__doctor__user').prefetch_related('payments')


class PaymentListView(generics.ListCreateAPIView):
    """API endpoint to list or create payments."""
    queryset = Payment.objects.select_related('invoice__patient__user').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PaymentCreateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        payment = serializer.save()
        # Update invoice status
        invoice = payment.invoice
        total_paid = invoice.payments.aggregate(Sum('amount'))['amount__sum'] or 0
        if total_paid >= invoice.total_amount:
            invoice.status = 'paid'
            invoice.payment_date = timezone.now()
            invoice.save()


class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update or delete a payment."""
    queryset = Payment.objects.select_related('invoice__patient__user').all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]


class RevenueReportView(generics.ListAPIView):
    """API endpoint to get revenue reports."""
    serializer_class = InvoiceSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = Invoice.objects.filter(status='paid')
        
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(payment_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(payment_date__date__lte=date_to)
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        total_revenue = queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_consultation = queryset.aggregate(Sum('consultation_fee'))['consultation_fee__sum'] or 0
        total_medicine = queryset.aggregate(Sum('medicine_cost'))['medicine_cost__sum'] or 0
        total_tests = queryset.aggregate(Sum('test_cost'))['test_cost__sum'] or 0
        
        return Response({
            'total_revenue': total_revenue,
            'total_consultation': total_consultation,
            'total_medicine': total_medicine,
            'total_tests': total_tests,
            'invoice_count': queryset.count(),
            'invoices': InvoiceSerializer(queryset, many=True).data
        })
