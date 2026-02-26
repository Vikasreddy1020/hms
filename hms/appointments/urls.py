"""URL configuration for appointments app."""
from django.urls import path
from .views import (
    AppointmentListView, AppointmentDetailView,
    AppointmentSlotListView, AppointmentSlotDetailView,
    AvailableSlotsView, MyAppointmentsView
)

urlpatterns = [
    path('', AppointmentListView.as_view(), name='appointment_list'),
    path('<int:pk>/', AppointmentDetailView.as_view(), name='appointment_detail'),
    path('slots/', AppointmentSlotListView.as_view(), name='slot_list'),
    path('slots/<int:pk>/', AppointmentSlotDetailView.as_view(), name='slot_detail'),
    path('available-slots/', AvailableSlotsView.as_view(), name='available_slots'),
    path('my-appointments/', MyAppointmentsView.as_view(), name='my_appointments'),
]
