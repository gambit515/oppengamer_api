from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    GetStudentByTelegramId,
    IsAuthorizedStudent,
    ActivateStudent,
    GetGroups,
    CreateGroup,
    CreateAttendance, GetAttendanceByGroup, GetStudentById,
    GetStudentsByGroup, ClearAttendance, ScheduleTaskViewSet
)

router = DefaultRouter()
router.register(r'schedule_tasks', ScheduleTaskViewSet, basename='schedule_task')

urlpatterns = [
    # Маршруты для студентов
    path('student/<int:telegram_id>/', GetStudentByTelegramId.as_view(), name='get_student_by_telegram_id'),
    path('student/id/<int:student_id>/', GetStudentById.as_view(), name='get_student_by_id'),
    path('is_authorized/<int:telegram_id>/', IsAuthorizedStudent.as_view(), name='is_authorized_student'),
    path('activate/', ActivateStudent.as_view(), name='activate_student'),

    # Маршруты для групп
    path('groups/', GetGroups.as_view(), name='get_groups'),
    path('create_group/', CreateGroup.as_view(), name='create_group'),
    path('group/<int:group_id>/', GetStudentsByGroup.as_view(), name='get_students_by_group'),
    path('attendance/<int:group_id>/clear/', ClearAttendance.as_view(), name='clear_attendance'),

    # Маршрут для регистрации присутствия
    path('attendance/', CreateAttendance.as_view(), name='create_attendance'),
    path('attendance/<int:group_id>/', GetAttendanceByGroup.as_view(), name='get_attendance_by_group'),

    path('', include(router.urls)),
]