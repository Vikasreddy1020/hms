"""API Root URL Configuration"""
from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """Root API endpoint showing available API paths."""
    return Response({
        'message': 'Welcome to Hospital Management System API',
        'version': '1.0',
        'endpoints': {
            'accounts': {
                'login': '/api/accounts/login/',
                'register': '/api/accounts/register/',
                'doctors': '/api/accounts/doctors/',
                'patients': '/api/accounts/patients/',
                'token_refresh': '/api/accounts/token/refresh/',
            },
            'appointments': '/api/appointments/',
            'prescriptions': '/api/prescriptions/',
            'billing': {
                'invoices': '/api/billing/invoices/',
                'payments': '/api/billing/payments/',
                'revenue': '/api/billing/revenue/',
            },
            'dashboard': {
                'admin': '/api/dashboard/admin/',
                'doctor': '/api/dashboard/doctor/',
                'patient': '/api/dashboard/patient/',
            },
            'admin_panel': '/admin/',
        },
        'documentation': 'See README.md for API documentation'
    })
