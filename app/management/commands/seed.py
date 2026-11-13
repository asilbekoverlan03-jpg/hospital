"""
python manage.py seed

Создаёт тестовые данные:
  - superuser admin / admin12345
  - 2 пациента (patient1, patient2)
  - 5 специализаций
  - 10 врачей с расписанием
  - несколько записей на приём (pending, confirmed, completed, cancelled)
  - медицинские карты для завершённых приёмов
  - отзывы
"""
import random
from datetime import time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import (
    UserProfile, Specialization, Doctor, Schedule,
    Appointment, MedicalRecord, DoctorReview
)


SPECIALIZATIONS = [
    {
        'name': 'Терапевт',
        'description': 'Первичная медицинская помощь, диагностика и лечение внутренних болезней.',
    },
    {
        'name': 'Кардиолог',
        'description': 'Диагностика и лечение заболеваний сердечно-сосудистой системы.',
    },
    {
        'name': 'Невролог',
        'description': 'Лечение заболеваний нервной системы: головная боль, остеохондроз, инсульт.',
    },
    {
        'name': 'Хирург',
        'description': 'Хирургическое лечение заболеваний, плановые и экстренные операции.',
    },
    {
        'name': 'Офтальмолог',
        'description': 'Диагностика и лечение заболеваний органов зрения.',
    },
]

DOCTORS = [
    {'first_name': 'Иван', 'last_name': 'Петров', 'patronymic': 'Сергеевич', 'experience_years': 15, 'price': 2500, 'spec': 'Терапевт'},
    {'first_name': 'Мария', 'last_name': 'Иванова', 'patronymic': 'Александровна', 'experience_years': 10, 'price': 3500, 'spec': 'Кардиолог'},
    {'first_name': 'Алексей', 'last_name': 'Смирнов', 'patronymic': 'Дмитриевич', 'experience_years': 20, 'price': 3000, 'spec': 'Невролог'},
    {'first_name': 'Ольга', 'last_name': 'Козлова', 'patronymic': 'Игоревна', 'experience_years': 8, 'price': 4000, 'spec': 'Хирург'},
    {'first_name': 'Дмитрий', 'last_name': 'Новиков', 'patronymic': 'Викторович', 'experience_years': 12, 'price': 2800, 'spec': 'Офтальмолог'},
    {'first_name': 'Елена', 'last_name': 'Морозова', 'patronymic': 'Павловна', 'experience_years': 18, 'price': 3200, 'spec': 'Терапевт'},
    {'first_name': 'Сергей', 'last_name': 'Волков', 'patronymic': 'Николаевич', 'experience_years': 7, 'price': 3800, 'spec': 'Кардиолог'},
    {'first_name': 'Анна', 'last_name': 'Алексеева', 'patronymic': 'Михайловна', 'experience_years': 14, 'price': 2600, 'spec': 'Невролог'},
    {'first_name': 'Николай', 'last_name': 'Лебедев', 'patronymic': 'Андреевич', 'experience_years': 22, 'price': 4500, 'spec': 'Хирург'},
    {'first_name': 'Татьяна', 'last_name': 'Семёнова', 'patronymic': 'Юрьевна', 'experience_years': 9, 'price': 2200, 'spec': 'Офтальмолог'},
]

# Расписание: каждый врач работает в рабочие дни (пн-пт)
WEEKDAYS = [1, 2, 3, 4, 5]


class Command(BaseCommand):
    help = 'Заполнить базу данных тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Начало заполнения базы данных...')

        # ── Суперпользователь ──────────────────────────────────────────────────
        admin, created = UserProfile.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@clinic.ru',
                'first_name': 'Администратор',
                'last_name': 'Системы',
                'is_staff': True,
                'is_superuser': True,
                'phone_number': '+7 (900) 000-00-01',
            }
        )
        if created:
            admin.set_password('admin12345')
            admin.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Суперпользователь admin создан'))
        else:
            self.stdout.write('  · Суперпользователь admin уже существует')

        # ── Пациенты ───────────────────────────────────────────────────────────
        patients = []
        patients_data = [
            {
                'username': 'patient1',
                'email': 'patient1@mail.ru',
                'first_name': 'Пётр',
                'last_name': 'Сидоров',
                'phone_number': '+7 (911) 111-11-11',
                'blood_group': 'A+',
                'address': 'г. Москва, ул. Ленина, д. 1',
            },
            {
                'username': 'patient2',
                'email': 'patient2@mail.ru',
                'first_name': 'Светлана',
                'last_name': 'Кузнецова',
                'phone_number': '+7 (922) 222-22-22',
                'blood_group': 'B-',
                'address': 'г. Москва, ул. Пушкина, д. 5',
            },
        ]
        for pd in patients_data:
            p, created = UserProfile.objects.get_or_create(
                username=pd['username'],
                defaults=pd
            )
            if created:
                p.set_password('Patient123!')
                p.save()
                self.stdout.write(self.style.SUCCESS(f'  ✓ Пациент {p.username} создан'))
            else:
                self.stdout.write(f'  · Пациент {p.username} уже существует')
            patients.append(p)

        # ── Специализации ─────────────────────────────────────────────────────
        spec_objects = {}
        for sd in SPECIALIZATIONS:
            spec, created = Specialization.objects.get_or_create(
                name=sd['name'],
                defaults={'description': sd['description']}
            )
            spec_objects[sd['name']] = spec
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Специализация «{spec.name}» создана'))

        # ── Врачи + Расписание ────────────────────────────────────────────────
        doctor_objects = []
        for dd in DOCTORS:
            doctor, created = Doctor.objects.get_or_create(
                first_name=dd['first_name'],
                last_name=dd['last_name'],
                defaults={
                    'patronymic': dd['patronymic'],
                    'experience_years': dd['experience_years'],
                    'price': dd['price'],
                    'specialization': spec_objects[dd['spec']],
                }
            )
            doctor_objects.append(doctor)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Врач {doctor} создан'))
                # Расписание: пн–пт 09:00–17:00
                for day in WEEKDAYS:
                    Schedule.objects.get_or_create(
                        doctor=doctor,
                        day_of_week=day,
                        defaults={
                            'start_time': time(9, 0),
                            'end_time': time(17, 0),
                        }
                    )

        # ── Записи на приём ────────────────────────────────────────────────────
        now = timezone.now()

        appointments_data = [
            # Завершённые (для отзывов и мед. карт)
            {
                'patient': patients[0],
                'doctor': doctor_objects[0],
                'date_time': now - timedelta(days=10, hours=2),
                'complaint': 'Общая слабость, кашель',
                'status': 'completed',
            },
            {
                'patient': patients[0],
                'doctor': doctor_objects[1],
                'date_time': now - timedelta(days=7, hours=3),
                'complaint': 'Боли в грудной клетке',
                'status': 'completed',
            },
            {
                'patient': patients[1],
                'doctor': doctor_objects[0],
                'date_time': now - timedelta(days=5, hours=1),
                'complaint': 'Высокая температура, насморк',
                'status': 'completed',
            },
            {
                'patient': patients[1],
                'doctor': doctor_objects[2],
                'date_time': now - timedelta(days=3, hours=4),
                'complaint': 'Головная боль, головокружение',
                'status': 'completed',
            },
            # Подтверждённые
            {
                'patient': patients[0],
                'doctor': doctor_objects[3],
                'date_time': now + timedelta(days=2, hours=2),
                'complaint': 'Боли в животе',
                'status': 'confirmed',
            },
            # Ожидают
            {
                'patient': patients[1],
                'doctor': doctor_objects[4],
                'date_time': now + timedelta(days=3, hours=3),
                'complaint': 'Снижение зрения',
                'status': 'pending',
            },
            {
                'patient': patients[0],
                'doctor': doctor_objects[5],
                'date_time': now + timedelta(days=5, hours=1),
                'complaint': 'Профилактический осмотр',
                'status': 'pending',
            },
            # Отменённые
            {
                'patient': patients[1],
                'doctor': doctor_objects[1],
                'date_time': now - timedelta(days=1, hours=2),
                'complaint': 'Аритмия',
                'status': 'cancelled',
            },
        ]

        created_appointments = []
        for ad in appointments_data:
            apt, created = Appointment.objects.get_or_create(
                patient=ad['patient'],
                doctor=ad['doctor'],
                date_time=ad['date_time'],
                defaults={
                    'complaint': ad['complaint'],
                    'status': ad['status'],
                }
            )
            created_appointments.append(apt)
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Приём: {apt.patient.username} → {apt.doctor} [{apt.status}]'
                ))

        # ── Медицинские карты для завершённых приёмов ─────────────────────────
        medical_data = [
            {
                'appointment': created_appointments[0],
                'diagnosis': 'ОРВИ средней тяжести',
                'prescription': 'Парацетамол 500мг 3р/день 5 дней. Обильное питьё.',
            },
            {
                'appointment': created_appointments[1],
                'diagnosis': 'Межрёберная невралгия',
                'prescription': 'Диклофенак 100мг 1р/день 7 дней. ЛФК.',
            },
            {
                'appointment': created_appointments[2],
                'diagnosis': 'Острый ринит',
                'prescription': 'Аквамарис 3р/день 7 дней. Отдых.',
            },
            {
                'appointment': created_appointments[3],
                'diagnosis': 'Вегетососудистая дистония',
                'prescription': 'Магний B6 1р/день 1 месяц. Снижение стресса.',
            },
        ]

        for md in medical_data:
            apt = md['appointment']
            if not hasattr(apt, 'medical_record') or not MedicalRecord.objects.filter(appointment=apt).exists():
                mr = MedicalRecord.objects.create(
                    appointment=apt,
                    diagnosis=md['diagnosis'],
                    prescription=md['prescription'],
                )
                self.stdout.write(self.style.SUCCESS(f'  ✓ Мед. карта для приёма {apt.id} создана'))

        # ── Отзывы ────────────────────────────────────────────────────────────
        reviews_data = [
            {
                'doctor': doctor_objects[0],
                'patient': patients[0],
                'stars': 5,
                'comment': 'Отличный врач! Очень внимательный, всё объяснил.',
            },
            {
                'doctor': doctor_objects[1],
                'patient': patients[0],
                'stars': 4,
                'comment': 'Хороший специалист, но пришлось подождать.',
            },
            {
                'doctor': doctor_objects[0],
                'patient': patients[1],
                'stars': 5,
                'comment': 'Профессионально, быстро поставили диагноз.',
            },
            {
                'doctor': doctor_objects[2],
                'patient': patients[1],
                'stars': 4,
                'comment': 'Грамотный невролог, рекомендую.',
            },
        ]

        for rd in reviews_data:
            review, created = DoctorReview.objects.get_or_create(
                doctor=rd['doctor'],
                patient=rd['patient'],
                defaults={
                    'stars': rd['stars'],
                    'comment': rd['comment'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Отзыв: {review.patient.username} → {review.doctor}: {review.stars}★'
                ))

        self.stdout.write(self.style.SUCCESS('\n✅ База данных успешно заполнена!'))
        self.stdout.write('')
        self.stdout.write('Учётные данные:')
        self.stdout.write('  admin / admin12345  (суперпользователь)')
        self.stdout.write('  patient1 / Patient123!  (пациент)')
        self.stdout.write('  patient2 / Patient123!  (пациент)')
