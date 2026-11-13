from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import (
    UserProfile, Specialization, Doctor, Schedule,
    Appointment, MedicalRecord, DoctorReview
)


# ─── Auth ────────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=UserProfile.objects.all(), message='Этот email уже занят.')]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='Подтверждение пароля')

    class Meta:
        model = UserProfile
        fields = [
            'username', 'password', 'password2', 'email',
            'first_name', 'last_name',
            'birth_date', 'phone_number', 'address', 'blood_group',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = UserProfile(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ─── UserProfile ─────────────────────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'birth_date', 'phone_number', 'address', 'blood_group', 'date_register',
        ]
        read_only_fields = ['id', 'username', 'date_register']


# ─── Specialization ───────────────────────────────────────────────────────────

class SpecializationSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=False, allow_null=True)

    class Meta:
        model = Specialization
        fields = ['id', 'name', 'description', 'image']


# ─── Schedule ─────────────────────────────────────────────────────────────────

class ScheduleSerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'doctor', 'day_of_week', 'day_of_week_display', 'start_time', 'end_time']


# ─── DoctorReview ─────────────────────────────────────────────────────────────

class DoctorReviewSerializer(serializers.ModelSerializer):
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())
    patient_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DoctorReview
        fields = ['id', 'doctor', 'patient', 'patient_name', 'stars', 'comment', 'created_date']
        read_only_fields = ['id', 'created_date']

    def get_patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username

    def validate(self, attrs):
        request = self.context.get('request')
        patient = request.user
        doctor = attrs.get('doctor')

        # Проверяем уникальность
        if DoctorReview.objects.filter(doctor=doctor, patient=patient).exists():
            raise serializers.ValidationError('Вы уже оставили отзыв этому врачу.')

        # Проверяем, что у пациента есть завершённый приём у этого врача
        has_completed = Appointment.objects.filter(
            patient=patient, doctor=doctor, status='completed'
        ).exists()
        if not has_completed:
            raise serializers.ValidationError(
                'Вы можете оставить отзыв только после завершённого приёма у этого врача.'
            )
        return attrs


# ─── Doctor ───────────────────────────────────────────────────────────────────

class DoctorListSerializer(serializers.ModelSerializer):
    specialization_name = serializers.CharField(source='specialization.name', read_only=True)
    avg_rating = serializers.SerializerMethodField()
    appointment_count = serializers.SerializerMethodField()
    photo = serializers.ImageField(use_url=True, required=False, allow_null=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'first_name', 'last_name', 'patronymic', 'photo',
            'experience_years', 'price', 'specialization', 'specialization_name',
            'avg_rating', 'appointment_count',
        ]

    def get_avg_rating(self, obj):
        return obj.get_avg_rating()

    def get_appointment_count(self, obj):
        return obj.get_appointment_count()


class DoctorDetailSerializer(DoctorListSerializer):
    schedules = ScheduleSerializer(many=True, read_only=True)
    reviews = DoctorReviewSerializer(many=True, read_only=True)
    specialization_detail = SpecializationSerializer(source='specialization', read_only=True)

    class Meta(DoctorListSerializer.Meta):
        fields = DoctorListSerializer.Meta.fields + [
            'schedules', 'reviews', 'specialization_detail',
        ]


# ─── MedicalRecord ────────────────────────────────────────────────────────────

class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ['id', 'appointment', 'diagnosis', 'prescription', 'created_date']
        read_only_fields = ['id', 'created_date']

    def validate_appointment(self, appointment):
        if appointment.status != 'completed':
            raise serializers.ValidationError(
                'Медицинская карта может быть создана только для завершённого приёма.'
            )
        if hasattr(appointment, 'medical_record'):
            raise serializers.ValidationError(
                'Для этого приёма уже существует медицинская карта.'
            )
        return appointment


# ─── Appointment ─────────────────────────────────────────────────────────────

class MedicalRecordInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ['id', 'diagnosis', 'prescription', 'created_date']


class AppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())
    patient_info = UserProfileSerializer(source='patient', read_only=True)
    doctor_info = DoctorListSerializer(source='doctor', read_only=True)
    medical_record = MedicalRecordInlineSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_info', 'doctor', 'doctor_info',
            'date_time', 'complaint', 'status', 'status_display',
            'created_date', 'medical_record',
        ]
        read_only_fields = ['id', 'status', 'created_date']

    def validate_date_time(self, value):
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError('Дата и время должны быть в будущем.')
        return value

    def validate(self, attrs):
        from django.utils import timezone

        doctor = attrs.get('doctor')
        date_time = attrs.get('date_time')

        if not doctor or not date_time:
            return attrs

        # Приводим к локальному времени
        import pytz
        from django.conf import settings as django_settings
        tz = pytz.timezone(django_settings.TIME_ZONE)
        local_dt = date_time.astimezone(tz)

        # день недели: Python isoweekday() возвращает 1=пн ... 7=вс
        day_of_week = local_dt.isoweekday()
        appointment_time = local_dt.time()

        # Проверяем расписание
        try:
            schedule = Schedule.objects.get(doctor=doctor, day_of_week=day_of_week)
        except Schedule.DoesNotExist:
            raise serializers.ValidationError(
                f'Врач не принимает в этот день недели.'
            )

        if not (schedule.start_time <= appointment_time <= schedule.end_time):
            raise serializers.ValidationError(
                f'Время приёма должно быть между {schedule.start_time} и {schedule.end_time}.'
            )

        # Проверяем, что слот не занят
        conflict = Appointment.objects.filter(
            doctor=doctor,
            date_time=date_time,
            status__in=['pending', 'confirmed']
        )
        # При обновлении исключаем себя
        if self.instance:
            conflict = conflict.exclude(pk=self.instance.pk)

        if conflict.exists():
            raise serializers.ValidationError(
                'Это время уже занято у данного врача. Выберите другое время.'
            )

        return attrs
