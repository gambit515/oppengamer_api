from django.urls import path
from .views import (
    GetStudentByTelegramId,
    IsAuthorizedStudent,
    ActivateStudent,
    GetGroups,
    CreateGroup,
    CreateAttendance, GetAttendanceByGroup  # Новое представление
)

urlpatterns = [
    # Маршруты для студентов
    path('student/<int:telegram_id>/', GetStudentByTelegramId.as_view(), name='get_student_by_telegram_id'),
    path('is_authorized/<int:telegram_id>/', IsAuthorizedStudent.as_view(), name='is_authorized_student'),
    path('activate/', ActivateStudent.as_view(), name='activate_student'),

    # Маршруты для групп
    path('groups/', GetGroups.as_view(), name='get_groups'),
    path('create_group/', CreateGroup.as_view(), name='create_group'),

    # Маршрут для регистрации присутствия
    path('attendance/', CreateAttendance.as_view(), name='create_attendance'),
    path('attendance/<int:group_id>/', GetAttendanceByGroup.as_view(), name='get_attendance_by_group'),
]