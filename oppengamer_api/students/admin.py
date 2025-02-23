from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import Group, Student, AttendanceRecord, ScheduleTask

# Админ-класс для модели Group
@admin.register(Group)
class GroupAdmin(GuardedModelAdmin):
    list_display = ('name', 'description', 'chat')  # Поля для отображения
    search_fields = ('name',)  # Поиск по названию группы
    ordering = ('name',)  # Сортировка по названию группы

# Админ-класс для модели Student
@admin.register(Student)
class StudentAdmin(GuardedModelAdmin):
    list_display = ('full_name', 'phone', 'telegram_id', 'active', 'group')  # Поля для отображения
    list_filter = ('active', 'group')  # Фильтры справа
    search_fields = ('name', 'surname', 'phone', 'telegram_id')  # Поиск по указанным полям
    ordering = ('surname', 'name')  # Сортировка по фамилии и имени

    def full_name(self, obj):
        return f"{obj.surname} {obj.name} {obj.patronymic or ''}".strip()

    full_name.short_description = 'Full Name'  # Название столбца в админке

# Админ-класс для модели AttendanceRecord
@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(GuardedModelAdmin):
    list_display = ('get_student_full_name', 'get_group_name', 'timestamp')  # Поля для отображения
    list_filter = ('group', 'timestamp')  # Фильтры справа
    search_fields = ('student__name', 'student__surname', 'group__name')  # Поиск по связанным полям
    ordering = ('-timestamp',)  # Сортировка по времени создания (от новых к старым)

    def get_student_full_name(self, obj):
        return f"{obj.student.surname} {obj.student.name}"

    get_student_full_name.short_description = 'Student'  # Название столбца в админке

    def get_group_name(self, obj):
        return obj.group.name if obj.group else None

    get_group_name.short_description = 'Group'  # Название столбца в админке

# Админ-класс для модели ScheduleTask
@admin.register(ScheduleTask)
class ScheduleTaskAdmin(GuardedModelAdmin):
    list_display = ('day', 'time', 'action', 'get_chat_id', 'group')  # Отображаемые поля в списке
    list_filter = ('day', 'action')  # Фильтры справа
    search_fields = ('group__name',)  # Поиск по имени группы
    ordering = ('day', 'time')  # Сортировка по дню и времени

    def get_chat_id(self, obj):
        return obj.group.chat if obj.group else None

    get_chat_id.short_description = 'Chat ID'  # Название столбца в админке