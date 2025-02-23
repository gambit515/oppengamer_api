from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from guardian.admin import GuardedModelAdmin
from .models import Group, Student, AttendanceRecord, ScheduleTask, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

# Расширяем стандартный UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Регистрируем UserAdmin с инлайном для профиля
admin.site.unregister(User)  # Сначала удаляем стандартную регистрацию User
admin.site.register(User, UserAdmin)


# Админ-класс для модели Group
@admin.register(Group)
class GroupAdmin(GuardedModelAdmin):
    list_display = ('name', 'description', 'chat')  # Поля для отображения
    search_fields = ('name',)  # Поиск по названию группы
    ordering = ('name',)  # Сортировка по названию группы

# Админ-класс для модели Student
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'telegram_id', 'active', 'group')

    def get_queryset(self, request):
        # Получаем базовый queryset
        qs = super().get_queryset(request)

        # Если пользователь — суперпользователь, показываем все записи
        if request.user.is_superuser:
            return qs

        # Иначе фильтруем по группе, связанной с UserProfile
        user_group = getattr(request.user, 'userprofile', None)
        if user_group and user_group.group:
            return qs.filter(group=user_group.group)
        return qs.none()  # Если группа не назначена, показываем пустой список

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Ограничиваем выбор группы при редактировании/создании студента
        if db_field.name == "group" and not request.user.is_superuser:
            user_group = getattr(request.user, 'userprofile', None)
            if user_group and user_group.group:
                kwargs["queryset"] = Group.objects.filter(id=user_group.group.id)
            else:
                kwargs["queryset"] = Group.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Student, StudentAdmin)

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
class ScheduleTaskAdmin(admin.ModelAdmin):
    list_display = ('day', 'time', 'action', 'group')

    def get_queryset(self, request):
        # Получаем базовый queryset
        qs = super().get_queryset(request)

        # Если пользователь — суперпользователь, показываем все записи
        if request.user.is_superuser:
            return qs

        # Иначе фильтруем по группе, связанной с UserProfile
        user_group = getattr(request.user, 'userprofile', None)
        if user_group and user_group.group:
            return qs.filter(group=user_group.group)
        return qs.none()  # Если группа не назначена, показываем пустой список

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Ограничиваем выбор группы при редактировании/создании задачи расписания
        if db_field.name == "group" and not request.user.is_superuser:
            user_group = getattr(request.user, 'userprofile', None)
            if user_group and user_group.group:
                kwargs["queryset"] = Group.objects.filter(id=user_group.group.id)
            else:
                kwargs["queryset"] = Group.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(ScheduleTask, ScheduleTaskAdmin)