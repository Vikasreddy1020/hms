"""Custom permissions for role-based access control."""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Allow access to admin users only."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsDoctor(permissions.BasePermission):
    """Allow access to doctors only."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_doctor


class IsPatient(permissions.BasePermission):
    """Allow access to patients only."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_patient


class IsDoctorOrReadOnly(permissions.BasePermission):
    """Allow doctors to edit, others can only read."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_doctor

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_doctor


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access to owners or admin users."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'patient') and hasattr(obj.patient, 'user'):
            return obj.patient.user == request.user
        if hasattr(obj, 'doctor') and hasattr(obj.doctor, 'user'):
            return obj.doctor.user == request.user
        return False
