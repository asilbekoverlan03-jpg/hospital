from django.contrib.auth import authenticate
from django.utils import timezone

from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    UserProfile, Specialization, Doctor, Schedule,
    Appointment, MedicalRecord, DoctorReview
)
from .serializers import (
    RegisterSerializer, UserProfileSerializer,
    SpecializationSerializer,
    DoctorListSerializer, DoctorDetailSerializer,
    ScheduleSerializer,
    AppointmentSerializer,
    MedicalRecordSerializer,
    DoctorReviewSerializer,
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin, IsPatientOwner
from .filters import DoctorFilter, AppointmentFilter


# ─── Auth ─────────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/"""
    queryset = UserProfile.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user, context={'request': request}).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """POST /api/auth/login/"""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Укажите имя пользователя и пароль.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(
                {'error': 'Неверные учётные данные.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user, context={'request': request}).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class LogoutView(APIView):
    """POST /api/auth/logout/ — занести refresh-токен в чёрный список."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'detail': 'Выход выполнен.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Выход выполнен.'}, status=status.HTTP_200_OK)


# ─── Profile ──────────────────────────────────────────────────────────────────

class ProfileView(generics.RetrieveUpdateAPIView):
    """GET / PATCH /api/profile/"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ─── Specializations ──────────────────────────────────────────────────────────

class SpecializationViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/specializations/, GET /api/specializations/{id}/"""
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [AllowAny]
    pagination_class = None  # Список специализаций без пагинации (обычно небольшой)


# ─── Doctors ──────────────────────────────────────────────────────────────────

class DoctorViewSet(viewsets.ModelViewSet):
    """
    GET  /api/doctors/         — список (AllowAny)
    GET  /api/doctors/{id}/    — детали (AllowAny)
    POST /api/doctors/         — создать (IsAdminUser)
    PUT/PATCH /api/doctors/{id}/ — изменить (IsAdminUser)
    DELETE /api/doctors/{id}/  — удалить (IsAdminUser)
    """
    queryset = Doctor.objects.select_related('specialization').prefetch_related(
        'schedules', 'reviews'
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DoctorFilter
    search_fields = ['first_name', 'last_name', 'patronymic']
    ordering_fields = ['price', 'experience_years', 'last_name']
    ordering = ['last_name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DoctorDetailSerializer
        return DoctorListSerializer


# ─── Schedules ────────────────────────────────────────────────────────────────

class ScheduleViewSet(viewsets.ModelViewSet):
    """
    GET /api/schedules/?doctor={id}
    """
    queryset = Schedule.objects.select_related('doctor')
    serializer_class = ScheduleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['doctor']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


# ─── Appointments ─────────────────────────────────────────────────────────────

class AppointmentViewSet(viewsets.ModelViewSet):
    """
    Пациент видит только свои, админ — все.
    POST — создание с валидацией расписания и слотов.
    POST /api/appointments/{id}/cancel/ — отмена своей записи.
    PATCH /api/appointments/{id}/ — смена статуса (только для админа).
    """
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AppointmentFilter
    ordering_fields = ['date_time', 'created_date']
    ordering = ['-date_time']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Appointment.objects.select_related(
            'patient', 'doctor', 'doctor__specialization'
        ).prefetch_related('medical_record')
        if user.is_staff:
            return qs
        return qs.filter(patient=user)

    def get_permissions(self):
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        """Только администратор может менять статус."""
        instance = self.get_object()
        if not request.user.is_staff:
            return Response(
                {'error': 'Недостаточно прав для смены статуса.'},
                status=status.HTTP_403_FORBIDDEN
            )
        allowed = {'status'}
        data = {k: v for k, v in request.data.items() if k in allowed}
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)

        new_status = data.get('status')
        if new_status and new_status not in ['confirmed', 'completed', 'cancelled', 'pending']:
            return Response(
                {'error': 'Недопустимый статус.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Обновляем статус напрямую, минуя валидацию расписания
        instance.status = new_status
        instance.save(update_fields=['status'])
        return Response(AppointmentSerializer(instance, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='cancel', permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """POST /api/appointments/{id}/cancel/"""
        appointment = self.get_object()

        # Проверяем, что это запись текущего пользователя
        if not request.user.is_staff and appointment.patient != request.user:
            return Response(
                {'error': 'Вы не можете отменить чужую запись.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if appointment.status in ['cancelled', 'completed']:
            return Response(
                {'error': f'Нельзя отменить запись со статусом «{appointment.get_status_display()}».'},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = 'cancelled'
        appointment.save(update_fields=['status'])
        return Response(AppointmentSerializer(appointment, context={'request': request}).data)


# ─── Medical Records ──────────────────────────────────────────────────────────

class MedicalRecordViewSet(viewsets.ModelViewSet):
    """
    Пациент видит только свои записи.
    Создавать может только администратор (для завершённых приёмов).
    """
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = MedicalRecord.objects.select_related(
            'appointment__patient', 'appointment__doctor'
        )
        if user.is_staff:
            return qs
        return qs.filter(appointment__patient=user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {'error': 'Создавать медицинские карты может только администратор.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {'error': 'Редактировать медицинские карты может только администратор.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {'error': 'Удалять медицинские карты может только администратор.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


# ─── Reviews ──────────────────────────────────────────────────────────────────

class DoctorReviewViewSet(viewsets.ModelViewSet):
    """
    GET  /api/reviews/?doctor={id}
    POST /api/reviews/ — только авторизованным, у кого есть завершённый приём
    """
    serializer_class = DoctorReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['doctor']
    ordering = ['-created_date']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return DoctorReview.objects.select_related('patient', 'doctor')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_staff and instance.patient != request.user:
            return Response(
                {'error': 'Вы можете редактировать только свои отзывы.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_staff and instance.patient != request.user:
            return Response(
                {'error': 'Вы можете удалять только свои отзывы.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
