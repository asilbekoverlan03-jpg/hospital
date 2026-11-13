from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(AbstractUser):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A (I) Rh+'),
        ('A-', 'A (I) Rh-'),
        ('B+', 'B (II) Rh+'),
        ('B-', 'B (II) Rh-'),
        ('AB+', 'AB (IV) Rh+'),
        ('AB-', 'AB (IV) Rh-'),
        ('O+', 'O (I) Rh+'),
        ('O-', 'O (I) Rh-'),
    ]

    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    address = models.TextField(blank=True, verbose_name='Адрес')
    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        blank=True,
        verbose_name='Группа крови'
    )
    date_register = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} ({self.get_full_name() or self.email})'


class Specialization(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(
        upload_to='specializations/',
        null=True,
        blank=True,
        verbose_name='Изображение'
    )

    class Meta:
        verbose_name = 'Специализация'
        verbose_name_plural = 'Специализации'
        ordering = ['name']

    def __str__(self):
        return self.name


class Doctor(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    photo = models.ImageField(
        upload_to='doctors/',
        null=True,
        blank=True,
        verbose_name='Фото'
    )
    experience_years = models.PositiveIntegerField(default=0, verbose_name='Опыт (лет)')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость приёма')
    specialization = models.ForeignKey(
        Specialization,
        on_delete=models.SET_NULL,
        null=True,
        related_name='doctors',
        verbose_name='Специализация'
    )

    class Meta:
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}'.strip()

    def get_avg_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return None
        total = sum(r.stars for r in reviews)
        return round(total / reviews.count(), 1)

    def get_appointment_count(self):
        return self.appointments.filter(
            status__in=['confirmed', 'completed']
        ).count()


class Schedule(models.Model):
    DAY_CHOICES = [
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
        (7, 'Воскресенье'),
    ]

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Врач'
    )
    day_of_week = models.IntegerField(choices=DAY_CHOICES, verbose_name='День недели')
    start_time = models.TimeField(verbose_name='Начало приёма')
    end_time = models.TimeField(verbose_name='Конец приёма')

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'
        ordering = ['day_of_week', 'start_time']
        unique_together = [('doctor', 'day_of_week')]

    def __str__(self):
        return f'{self.doctor} — {self.get_day_of_week_display()} {self.start_time}–{self.end_time}'


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждён'),
        ('cancelled', 'Отменён'),
        ('completed', 'Завершён'),
    ]

    patient = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Пациент'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Врач'
    )
    date_time = models.DateTimeField(verbose_name='Дата и время')
    complaint = models.TextField(verbose_name='Жалоба')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Запись на приём'
        verbose_name_plural = 'Записи на приём'
        ordering = ['-date_time']

    def __str__(self):
        return f'{self.patient} → {self.doctor} [{self.date_time:%d.%m.%Y %H:%M}]'


class MedicalRecord(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='medical_record',
        verbose_name='Приём'
    )
    diagnosis = models.TextField(verbose_name='Диагноз')
    prescription = models.TextField(verbose_name='Назначения')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Медицинская карта'
        verbose_name_plural = 'Медицинские карты'

    def __str__(self):
        return f'Карта: {self.appointment}'


class DoctorReview(models.Model):
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Врач'
    )
    patient = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Пациент'
    )
    stars = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка'
    )
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = [('doctor', 'patient')]
        ordering = ['-created_date']

    def __str__(self):
        return f'{self.patient} → {self.doctor}: {self.stars}★'
