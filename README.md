# Клиника

Сайт медицинской клиники: врачи, специализации и запись на приём.

## Стек

- **Backend:** Python 3.12, Django 4.2, Django REST Framework, SimpleJWT
- **Frontend:** React 18, Vite 6, Axios, React Router DOM

## Возможности

- Список специализаций с фотографиями
- Список врачей с фото, опытом, стоимостью приёма и рейтингом
- Страница врача: расписание по дням недели, отзывы пациентов
- Запись на приём: выбор врача, даты и времени, описание жалобы
- Валидация: дата в будущем, день и время входят в расписание врача, слот не занят
- Личный кабинет пациента: история приёмов, статусы, отмена записи
- Медицинские карты: диагноз и назначения для завершённых приёмов
- Регистрация и вход (JWT-токены), редактирование профиля
- Отзывы доступны только пациентам с завершённым приёмом у данного врача
- Адаптивный дизайн

## Модели

| Модель | Описание |
|---|---|
| `UserProfile` | Пациент (AbstractUser): дата рождения, телефон, адрес, группа крови |
| `Specialization` | Специализация врача: название, описание, фото |
| `Doctor` | Врач: ФИО, фото, опыт, стоимость, специализация |
| `Schedule` | Расписание врача: день недели, начало и конец приёма |
| `Appointment` | Запись на приём: пациент, врач, дата/время, жалоба, статус |
| `MedicalRecord` | Медицинская карта: диагноз и назначения для завершённого приёма |
| `DoctorReview` | Отзыв пациента о враче: оценка (1–5), комментарий |

## Запуск

### Backend (Windows PowerShell)

```powershell
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Применить миграции
python manage.py migrate

# 3. Заполнить тестовыми данными (опционально)
python manage.py seed

# 4. Запустить сервер на порту 8004
python manage.py runserver 8004
```

Доступно на: http://localhost:8004  
Админка: http://localhost:8004/admin/

Тестовые учётные данные (после `seed`):
- `admin` / `admin12345` — суперпользователь
- `patient1` / `Patient123!` — пациент
- `patient2` / `Patient123!` — пациент

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Доступно на: http://localhost:5173

### Переменные окружения

Скопируй `.env.example` → `.env` в корне проекта:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
```

Для фронтенда скопируй `frontend/.env.example` → `frontend/.env`:

```
VITE_API_URL=http://localhost:8004/api
```

## API-эндпоинты

```
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/logout/
GET    /api/profile/
PATCH  /api/profile/

GET    /api/specializations/
GET    /api/doctors/          ?search= &specialization= &ordering=
GET    /api/doctors/{id}/
GET    /api/schedules/        ?doctor=
GET    /api/appointments/
POST   /api/appointments/
POST   /api/appointments/{id}/cancel/
GET    /api/medical-records/
GET    /api/reviews/          ?doctor=
POST   /api/reviews/
```

## Что сделал я

- Модели и REST API на Django REST Framework
- Подключение API к фронтенду на React
