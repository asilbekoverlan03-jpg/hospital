import django_filters
from .models import Doctor, Appointment


class DoctorFilter(django_filters.FilterSet):
    specialization = django_filters.NumberFilter(field_name='specialization__id')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_experience = django_filters.NumberFilter(field_name='experience_years', lookup_expr='gte')

    class Meta:
        model = Doctor
        fields = ['specialization', 'min_price', 'max_price', 'min_experience']


class AppointmentFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status')
    doctor = django_filters.NumberFilter(field_name='doctor__id')
    date_from = django_filters.DateFilter(field_name='date_time', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='date_time', lookup_expr='date__lte')

    class Meta:
        model = Appointment
        fields = ['status', 'doctor', 'date_from', 'date_to']
