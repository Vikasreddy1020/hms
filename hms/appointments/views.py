"""Views for appointments app."""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Appointment, AppointmentSlot
from .serializers import (
    AppointmentSerializer, AppointmentCreateSerializer,
    AppointmentSlotSerializer, AppointmentStatusUpdateSerializer
)
from accounts.permissions import IsAdminUser, IsDoctor, IsPatient, IsOwnerOrAdmin


class AppointmentListView(generics.ListCreateAPIView):
    """API endpoint to list or create appointments."""
    queryset = Appointment.objects.select_related('patient__user', 'doctor__user').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Filter based on user role
        if user.is_patient:
            queryset = queryset.filter(patient__user=user)
        elif user.is_doctor:
            queryset = queryset.filter(doctor__user=user)
        
        # Additional filters
        status_filter = self.request.query_params.get('status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if date_from:
            queryset = queryset.filter(appointment_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(appointment_date__date__lte=date_to)
        
        return queryset

    def perform_create(self, serializer):
        if self.request.user.is_patient:
            patient = self.request.user.patient_profile
            serializer.save(patient=patient)
        else:
            serializer.save()


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update or delete an appointment."""
    queryset = Appointment.objects.select_related('patient__user', 'doctor__user').all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AppointmentStatusUpdateSerializer
        return AppointmentSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if updating status
        if 'status' in request.data:
            new_status = request.data.get('status')
            if new_status == 'cancelled' and not instance.can_cancel:
                return Response(
                    {'error': 'This appointment cannot be cancelled'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.can_cancel:
            return Response(
                {'error': 'This appointment cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.status = 'cancelled'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AppointmentSlotListView(generics.ListCreateAPIView):
    """API endpoint to list or create appointment slots."""
    queryset = AppointmentSlot.objects.select_related('doctor__user').all()
    serializer_class = AppointmentSlotSerializer
    permission_classes = [IsAdminUser]


class AppointmentSlotDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update or delete an appointment slot."""
    queryset = AppointmentSlot.objects.select_related('doctor__user').all()
    serializer_class = AppointmentSlotSerializer
    permission_classes = [IsAdminUser]


class AvailableSlotsView(generics.ListAPIView):
    """API endpoint to get available slots for a doctor."""
    serializer_class = AppointmentSlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        doctor_id = self.request.query_params.get('doctor_id')
        if doctor_id:
            return AppointmentSlot.objects.filter(
                doctor_id=doctor_id,
                is_available=True
            ).select_related('doctor__user')
        return AppointmentSlot.objects.none()


class MyAppointmentsView(generics.ListAPIView):
    """API endpoint to get current user's appointments."""
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_patient:
            return Appointment.objects.filter(
                patient__user=user
            ).select_related('patient__user', 'doctor__user')
        elif user.is_doctor:
            return Appointment.objects.filter(
                doctor__user=user
            ).select_related('patient__user', 'doctor__user')
        return Appointment.objects.none()
