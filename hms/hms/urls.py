"""
URL configuration for HMS project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from api_urls import api_root

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('doctor-dashboard/', TemplateView.as_view(template_name='doctor_dashboard.html'), name='doctor_dashboard'),
    path('patient-dashboard/', TemplateView.as_view(template_name='patient_dashboard.html'), name='patient_dashboard'),
    path('admin-dashboard/', TemplateView.as_view(template_name='admin_dashboard.html'), name='admin_dashboard'),
    path('api/', api_root, name='api_root'),
    path('api/accounts/', include('accounts.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/prescriptions/', include('prescriptions.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
