"""URL configuration for billing app."""
from django.urls import path
from .views import (
    InvoiceListView, InvoiceDetailView, MyInvoicesView,
    PaymentListView, PaymentDetailView, RevenueReportView
)

urlpatterns = [
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('my-invoices/', MyInvoicesView.as_view(), name='my_invoices'),
    path('payments/', PaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
    path('revenue/', RevenueReportView.as_view(), name='revenue_report'),
]
