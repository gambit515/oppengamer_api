from django.contrib import admin
from .models import Group, Student

# Регистрация модели Group
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Поля, которые будут отображаться в списке
    search_fields = ('name',)  # Поиск по названию группы
    ordering = ('name',)  # Сортировка по названию группы

# Регистрация модели Student
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'telegram_id', 'active', 'group')  # Поля для отображения
    list_filter = ('active', 'group')  # Фильтры справа
    search_fields = ('name', 'surname', 'phone', 'telegram_id')  # Поиск по указанным полям
    ordering = ('surname', 'name')  # Сортировка по фамилии и имени
    readonly_fields = ('student_id',)  # Поле student_id будет только для чтения

    def full_name(self, obj):
        return f"{obj.surname} {obj.name} {obj.patronymic or ''}".strip()
    full_name.short_description = 'Full Name'  # Название столбца в админкеа