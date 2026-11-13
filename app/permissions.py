from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Чтение — всем, запись — только администраторам."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """Только владелец объекта или администратор."""

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        # Для Appointment — проверяем patient
        if hasattr(obj, 'patient'):
            return obj.patient == request.user
        # Для DoctorReview — проверяем patient
        if hasattr(obj, 'patient'):
            return obj.patient == request.user
        return False


class IsPatientOwner(BasePermission):
    """Пациент видит только свои объекты."""

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        if hasattr(obj, 'patient'):
            return obj.patient == request.user
        if hasattr(obj, 'appointment'):
            return obj.appointment.patient == request.user
        return False
