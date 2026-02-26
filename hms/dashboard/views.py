"""Views for dashboard app with Redis caching."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Count, Sum, Avg, Q
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, Doctor, Patient
from appointments.models import Appointment
from appointments.serializers import AppointmentSerializer
from billing.models import Invoice
from prescriptions.models import Prescription
from accounts.permissions import IsAdminUser


class AdminDashboardView(APIView):
    """API endpoint for admin dashboard statistics."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        cache_key = 'admin_dashboard_stats'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)

        # Get date range from query params or use default (last 30 days)
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        # User statistics
        total_users = User.objects.count()
        total_doctors = User.objects.filter(role='doctor').count()
        total_patients = User.objects.filter(role='patient').count()
        new_users = User.objects.filter(date_joined__gte=start_date).count()

        # Appointment statistics
        total_appointments = Appointment.objects.filter(created_at__gte=start_date).count()
        completed_appointments = Appointment.objects.filter(
            status='completed', created_at__gte=start_date
        ).count()
        cancelled_appointments = Appointment.objects.filter(
            status='cancelled', created_at__gte=start_date
        ).count()

        # Revenue statistics
        total_revenue = Invoice.objects.filter(
            status='paid', payment_date__gte=start_date
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        pending_payments = Invoice.objects.filter(
            status='pending'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # Appointment by status
        appointments_by_status = Appointment.objects.values('status').annotate(
            count=Count('id')
        )

        # Appointment by doctor (top 5)
        top_doctors = Appointment.objects.values(
            'doctor__user__first_name', 'doctor__user__last_name', 'doctor__specialization'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        data = {
            'users': {
                'total': total_users,
                'doctors': total_doctors,
                'patients': total_patients,
                'new_users': new_users,
            },
            'appointments': {
                'total': total_appointments,
                'completed': completed_appointments,
                'cancelled': cancelled_appointments,
                'by_status': list(appointments_by_status),
            },
            'revenue': {
                'total': float(total_revenue),
                'pending': float(pending_payments),
                'period_days': days,
            },
            'top_doctors': list(top_doctors),
        }

        # Cache for 5 minutes
        cache.set(cache_key, data, 300)
        
        return Response(data)


class DoctorDashboardView(APIView):
    """API endpoint for doctor dashboard statistics."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_doctor:
            return Response(
                {'error': 'Only doctors can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            doctor = request.user.doctor_profile
        except Doctor.DoesNotExist:
            return Response({
                'today_appointments': 0,
                'upcoming_appointments': [],
                'total_patients': 0,
                'completed_appointments': 0,
                'monthly_revenue': 0,
                'message': 'Doctor profile not found. Please contact admin.'
            })

        cache_key = f'doctor_dashboard_{request.user.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)

        today = timezone.now().date()

        # Today's appointments
        today_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__date=today
        ).select_related('patient__user')

        # Upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__gte=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).select_related('patient__user')[:5]

        # Total patients
        total_patients = Appointment.objects.filter(
            doctor=doctor
        ).values('patient').distinct().count()

        # Completed appointments
        completed_count = Appointment.objects.filter(
            doctor=doctor, status='completed'
        ).count()

        # This month's revenue
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
        monthly_revenue = Invoice.objects.filter(
            appointment__doctor=doctor,
            status='paid',
            payment_date__gte=month_start
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        data = {
            'today_appointments': today_appointments.count(),
            'upcoming_appointments': AppointmentSerializer(upcoming_appointments, many=True).data,
            'total_patients': total_patients,
            'completed_appointments': completed_count,
            'monthly_revenue': float(monthly_revenue),
        }

        # Cache for 5 minutes
        cache.set(cache_key, data, 300)
        
        return Response(data)


class PatientDashboardView(APIView):
    """API endpoint for patient dashboard statistics."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_patient:
            return Response(
                {'error': 'Only patients can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        cache_key = f'patient_dashboard_{request.user.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)

        try:
            patient = request.user.patient_profile
        except Patient.DoesNotExist:
            return Response({
                'upcoming_appointments': [],
                'past_appointments': [],
                'total_visits': 0,
                'prescriptions': 0,
                'pending_bills': 0,
                'message': 'Patient profile not found. Please contact admin.'
            })

        # Upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            patient=patient,
            appointment_date__gte=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).select_related('doctor__user')[:5]

        # Past appointments
        past_appointments = Appointment.objects.filter(
            patient=patient,
            appointment_date__lt=timezone.now()
        ).select_related('doctor__user')[:5]

        # Total visits
        total_visits = Appointment.objects.filter(
            patient=patient, status='completed'
        ).count()

        # Prescriptions
        prescriptions = Prescription.objects.filter(
            patient=patient
        ).count()

        # Pending bills
        pending_bills = Invoice.objects.filter(
            patient=patient, status='pending'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        data = {
            'upcoming_appointments': AppointmentSerializer(upcoming_appointments, many=True).data,
            'past_appointments': AppointmentSerializer(past_appointments, many=True).data,
            'total_visits': total_visits,
            'prescriptions': prescriptions,
            'pending_bills': float(pending_bills),
        }

        # Cache for 5 minutes
        cache.set(cache_key, data, 300)
        
        return Response(data)
