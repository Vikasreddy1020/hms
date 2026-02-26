from django.contrib import admin
from .models import Invoice, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'patient', 'total_amount', 'status', 'payment_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['invoice_number', 'patient__user__username', 'patient__user__email']
    readonly_fields = ['invoice_number', 'total_amount', 'created_at', 'updated_at']
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice', 'amount', 'payment_method', 'transaction_id', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['invoice__invoice_number', 'transaction_id']
