"""URL configuration for prescriptions app."""
from django.urls import path
from .views import PrescriptionListView, PrescriptionDetailView, MyPrescriptionsView

urlpatterns = [
    path('', PrescriptionListView.as_view(), name='prescription_list'),
    path('<int:pk>/', PrescriptionDetailView.as_view(), name='prescription_detail'),
    path('my-prescriptions/', MyPrescriptionsView.as_view(), name='my_prescriptions'),
]
