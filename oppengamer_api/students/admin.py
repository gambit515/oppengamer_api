from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Group, Student, AttendanceRecord, ScheduleTask

class StudentAdmin(GuardedModelAdmin):
    list_display = ('name', 'surname', 'group')

class ScheduleTaskAdmin(GuardedModelAdmin):
    list_display = ('day', 'time', 'action', 'group')

admin.site.register(Student, StudentAdmin)
admin.site.register(ScheduleTask, ScheduleTaskAdmin)

# Регистрация модели Group
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'chat')  # Поля для отображения
    search_fields = ('name',)  # Поиск по названию группы
    ordering = ('name',)  # Сортировка по названию группы

# Регистрация модели Student
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'telegram_id', 'active', 'group')  # Поля для отображения
    list_filter = ('active', 'group')  # Фильтры справа
    search_fields = ('name', 'surname', 'phone', 'telegram_id')  # Поиск по указанным полям
    ordering = ('surname', 'name')  # Сортировка по фамилии и имени

    def full_name(self, obj):
        return f"{obj.surname} {obj.name} {obj.patronymic or ''}".strip()
    full_name.short_description = 'Full Name'  # Название столбца в админке

# Регистрация модели AttendanceRecord
@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'timestamp')  # Поля для отображения
    list_filter = ('group', 'timestamp')  # Фильтры справа
    search_fields = ('student__name', 'student__surname', 'group__name')  # Поиск по связанным полям
    ordering = ('-timestamp',)  # Сортировка по времени создания (от новых к старым)

    def student(self, obj):
        return f"{obj.student.surname} {obj.student.name}"  # Отображение полного имени студента
    student.short_description = 'Student'

    def group(self, obj):
        return obj.group.name if obj.group else None  # Отображение названия группы
    group.short_description = 'Group'


@admin.register(ScheduleTask)
class ScheduleTaskAdmin(admin.ModelAdmin):
    list_display = ('day', 'time', 'action', 'chat_id', 'group')  # Отображаемые поля в списке
    list_filter = ('day', 'action')  # Фильтры справа
    search_fields = ('group__name',)  # Поиск по имени группы
    ordering = ('day', 'time')  # Сортировка по дню и времени