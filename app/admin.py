from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    UserProfile, Specialization, Doctor, Schedule,
    Appointment, MedicalRecord, DoctorReview
)


@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'blood_group', 'is_staff']
    list_filter = ['is_staff', 'is_active', 'blood_group']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {
            'fields': ('birth_date', 'phone_number', 'address', 'blood_group')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {
            'fields': ('email', 'first_name', 'last_name', 'birth_date', 'phone_number', 'address', 'blood_group')
        }),
    )


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 1


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'patronymic', 'specialization', 'experience_years', 'price']
    list_filter = ['specialization', 'experience_years']
    search_fields = ['first_name', 'last_name', 'patronymic']
    inlines = [ScheduleInline]
    ordering = ['last_name', 'first_name']


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time']
    list_filter = ['day_of_week', 'doctor']
    search_fields = ['doctor__first_name', 'doctor__last_name']


class MedicalRecordInline(admin.StackedInline):
    model = MedicalRecord
    extra = 0
    can_delete = False


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date_time', 'status', 'created_date']
    list_filter = ['status', 'doctor', 'date_time']
    search_fields = ['patient__username', 'patient__first_name', 'patient__last_name',
                     'doctor__first_name', 'doctor__last_name']
    ordering = ['-date_time']
    inlines = [MedicalRecordInline]
    readonly_fields = ['created_date']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'doctor')


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'created_date']
    search_fields = ['appointment__patient__username', 'diagnosis']
    readonly_fields = ['created_date']


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'patient', 'stars', 'created_date']
    list_filter = ['stars', 'doctor']
    search_fields = ['patient__username', 'doctor__first_name', 'doctor__last_name', 'comment']
    readonly_fields = ['created_date']
