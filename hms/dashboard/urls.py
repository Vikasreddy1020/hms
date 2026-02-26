"""URL configuration for dashboard app."""
from django.urls import path
from .views import AdminDashboardView, DoctorDashboardView, PatientDashboardView

urlpatterns = [
    path('admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('doctor/', DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('patient/', PatientDashboardView.as_view(), name='patient_dashboard'),
]
