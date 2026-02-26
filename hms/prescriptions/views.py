"""Views for prescriptions app."""
from rest_framework import generics, permissions
from django.db.models import Q
from .models import Prescription
from .serializers import PrescriptionSerializer, PrescriptionCreateSerializer, PrescriptionUpdateSerializer
from accounts.permissions import IsAdminUser, IsDoctor, IsPatient, IsOwnerOrAdmin


class PrescriptionListView(generics.ListCreateAPIView):
    """API endpoint to list or create prescriptions."""
    queryset = Prescription.objects.select_related(
        'patient__user', 'doctor__user', 'appointment'
    ).prefetch_related('medicines').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PrescriptionCreateSerializer
        return PrescriptionSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_patient:
            queryset = queryset.filter(patient__user=user)
        elif user.is_doctor:
            queryset = queryset.filter(doctor__user=user)
        
        return queryset

    def perform_create(self, serializer):
        if self.request.user.is_doctor:
            doctor = self.request.user.doctor_profile
            serializer.save(doctor=doctor)


class PrescriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update or delete a prescription."""
    queryset = Prescription.objects.select_related(
        'patient__user', 'doctor__user', 'appointment'
    ).prefetch_related('medicines').all()
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PrescriptionUpdateSerializer
        return PrescriptionSerializer


class MyPrescriptionsView(generics.ListAPIView):
    """API endpoint to get current user's prescriptions."""
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_patient:
            return Prescription.objects.filter(
                patient__user=user
            ).select_related('patient__user', 'doctor__user', 'appointment').prefetch_related('medicines')
        elif user.is_doctor:
            return Prescription.objects.filter(
                doctor__user=user
            ).select_related('patient__user', 'doctor__user', 'appointment').prefetch_related('medicines')
        return Prescription.objects.none()
