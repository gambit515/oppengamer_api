from django.contrib.auth.models import User
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    chat = models.BigIntegerField(null=True, blank=True)  # ID чата Telegram
    thread_id = models.BigIntegerField(null=True, blank=True)  # ID темы (топика)

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    patronymic = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20, unique=True)
    student_id = models.AutoField(primary_key=True)  # ID студента
    telegram_id = models.BigIntegerField(null=True, blank=True)
    active = models.BooleanField(default=False)
    rights = models.CharField(max_length=50, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    def __str__(self):
        return f"{self.surname} {self.name}"

    @property
    def full_name(self):
        return f"{self.surname} {self.name} {self.patronymic or ''}".lower()


class AttendanceRecord(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} in {self.group} at {self.timestamp}"


class ScheduleTask(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    ACTION_CHOICES = [
        ('start', 'Start Attendance'),
        ('finalize', 'Finalize Attendance'),
    ]

    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    time = models.TimeField()
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='schedule_tasks')

    def __str__(self):
        return f"{self.day} {self.time} - {self.action}"

    @property
    def chat_id(self):
        """Возвращает chat_id из связанной группы."""
        if self.group:
            return self.group.chat
        return None


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.group.name if self.group else 'No Group'}"